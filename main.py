#!/usr/bin/env python3
"""
AI Job Hunter - Master Automation Pipeline
=======================================

This orchestrates the complete job hunting automation pipeline for ALL Roles:
1. Loops through every role in role_profiles.yaml sequentially.
2. Applies Role-aware Gemini AI-powered scoring.
3. Automatically persists to the SQLite App Tracker Database.
4. Schedules continuously for autonomous zero-touch monitoring.
"""

import os
import sys
import json
import time
import signal
import logging
from datetime import datetime, timezone
from pathlib import Path
import argparse

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.role_loader import load_role_profiles, validate_profile
from automation.hourly_scraper import JobPipeline
from database.engine import init_db

# Setup logging
log_dir = Path('data/ci')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'master_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def pre_flight_check():
    """Verify all required environment variables are set."""
    required = [
        'DATABASE_URL',
        'GEMINI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    missing = [v for v in required if not os.getenv(v)]
    
    if missing:
        logger.error(f"❌ CRITICAL ERROR: Missing environment variables: {', '.join(missing)}")
        logger.error("Please add these to GitHub Secrets (Settings > Secrets and variables > Actions).")
        return False
    
    logger.info("✅ Environment check passed.")
    return True

# Global flag for graceful shutdown
_running = True

def handle_signal(sig, frame):
    global _running
    logger.info("\nShutdown signal received... finishing current role safely before exit.")
    _running = False

def run_pipeline_for_all_roles():
    """Execute the job hunter pipeline across ALL defined roles."""
    roles, default_role = load_role_profiles()
    
    logger.info(f"🚀 Loaded {len(roles)} roles from configuration: {list(roles.keys())}")
    
    run_profile = os.getenv('RUN_PROFILE', 'hourly')
    job_window = os.getenv('JOB_WINDOW', '24h')
    
    results = {}
    total_new_jobs = 0

    for role_key, profile_data in roles.items():
        if not _running:
            logger.warning("Pipeline interupted gracefully.")
            break
            
        logger.info(f"\n======================================")
        logger.info(f"🔄 Processing Role: {role_key}")
        logger.info(f"======================================")
        
        # Prepare valid profile mapping directly like load_role_profile used to
        profile = dict(profile_data)
        profile["role_key"] = role_key
        profile["default_role"] = default_role
        
        try:
            validate_profile(profile, role_key)
            
            pipeline = JobPipeline(profile, run_profile=run_profile, job_window=job_window)
            result = pipeline.run()
            results[role_key] = result
            new_jobs = result.get('new_jobs', 0)
            total_new_jobs += new_jobs
            logger.info(f"✅ Completed role {role_key} - Found {new_jobs} new jobs.")
            
            # Send Telegram Alert if there are new jobs
            if new_jobs > 0:
                tel_token = os.getenv('TELEGRAM_BOT_TOKEN')
                chat_id = os.getenv('TELEGRAM_CHAT_ID')
                if tel_token and chat_id:
                    import requests
                    msg = f"🔥 *Pipeline Update*\n\nScraped **{new_jobs}** new highly-matching jobs for `{profile.get('display_name', role_key)}`.\n\n"
                    
                    top_jobs = result.get('top_jobs', [])
                    if top_jobs:
                        msg += "*💼 Top Picks:*\n"
                        for j in top_jobs:
                            pkg = j.get('salary_text', 'Not disclosed').strip() or 'Not disclosed'
                            msg += f"• *{j.get('title', 'Role')}* at {j.get('company', 'Company')}\n"
                            msg += f"  💰 Package: {pkg}\n"
                            if j.get('link'):
                                msg += f"  🔗 [Apply]({j.get('link')})\n\n"
                                
                    msg += "Open your Bot and type `/jobs` to review and track them instantly!"
                    
                    try:
                        requests.post(
                            f"https://api.telegram.org/bot{tel_token}/sendMessage",
                            json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"},
                            timeout=5
                        )
                    except Exception as t_err:
                        logger.warning(f"Failed to send telegram update: {t_err}")

        except Exception as e:
            logger.error(f"❌ Failed processing role '{role_key}': {e}", exc_info=True)
            results[role_key] = {"error": str(e), "success": False}
            
        # Give a short backoff between scraping entire roles to avoid heavy bot detection!
        time.sleep(5)

    return results, total_new_jobs

def main():
    parser = argparse.ArgumentParser(description='AI Job Hunter Master Orchestrator')
    parser.add_argument('--once', action='store_true', help='Run through all roles once and exit (for CI/CD)')
    parser.add_argument('--interval', type=int, default=180, help='Continuous interval in minutes (default 3 hours)')
    args = parser.parse_args()

    # Graceful shutdown handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    logger.info("====================================")
    logger.info("Initializing Master Job Pipeline...")
    logger.info("====================================")

    # 1. Environment Check
    if not pre_flight_check():
        return 1

    # 2. Initialize Database Tables
    try:
        logger.info("Initializing Database...")
        init_db()
        logger.info("✅ Database Ready.")
    except Exception as db_err:
        logger.error(f"❌ Database Initialization Failed: {db_err}")
        return 1

    if args.once:
        logger.info("Running in Single-Execution Mode (--once)")
        results, total = run_pipeline_for_all_roles()
        failed = [k for k, v in results.items() if 'error' in v or v.get('success') is False]
        
        logger.info(f"\nSummary: {len(results)} roles processed, {total} new jobs found.")
        if failed:
            logger.warning(f"⚠️ Some roles failed: {', '.join(failed)}")
            return 1 # Mark as failed in CI if any role failed
            
        return 0
        
    else:
        logger.info(f"Running in Continuous Mode (Interval: {args.interval} minutes)")
        cycle_count = 0
        
        while _running:
            cycle_count += 1
            logger.info(f"\n--- Starting Cycle #{cycle_count} ---")
            
            # Execute master loop
            run_pipeline_for_all_roles()
            
            if not _running:
                break
                
            # Cleanup old daily storage safely
            try:
                from automation.daily_storage import DailyStorage
                DailyStorage.cleanup_old_files(days_to_keep=30)
            except Exception as e:
                logger.warning(f"Storage cleanup failed: {e}")

            # Sleep
            logger.info(f"💤 Cycle #{cycle_count} done. Sleeping for {args.interval} minutes...")
            sleep_seconds = args.interval * 60
            
            # Sleep in chunks so we can interrupt it cleanly if needed
            while sleep_seconds > 0 and _running:
                time.sleep(1)
                sleep_seconds -= 1
                
        logger.info("Goodbye! Master Orchestrator shut down cleanly.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
