#!/usr/bin/env python3
"""
AI Job Hunter - Cloud Entry Point
Runs on cloud platforms (Render, Railway, GitHub Actions)
No local machine needed - fully automated 24/7
"""

import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Setup logging to file AND console
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cloud_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('.env-analyst')
except ImportError:
    logger.warning("⚠️ python-dotenv not installed, using system env vars")

def verify_config():
    """Verify all required environment variables are set"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH',
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"❌ Missing environment variables: {', '.join(missing)}")
        logger.error("Please set these in your cloud platform's environment variables")
        return False
    
    logger.info("✅ All environment variables verified")
    return True

def run_one_cycle():
    """Run one complete scraping cycle"""
    cycle_start = datetime.now()
    logger.info("=" * 60)
    logger.info(f"🤖 Starting AI Job Hunter - Cloud Mode")
    logger.info(f"⏰ Time: {cycle_start}")
    logger.info(f"📍 Environment: CLOUD")
    logger.info("=" * 60)
    
    try:
        # Verify configuration first
        if not verify_config():
            return False
        
        # Import scrapers
        try:
            from config.role_loader import load_role_profile
            from scrapers.common import scrape_jobs_for_profile
        except ImportError as e:
            logger.error(f"❌ Cannot import scrapers: {str(e)}")
            return False
        
        # Run scraping cycle
        logger.info("📍 Starting job scraper cycle...")
        try:
            profile = load_role_profile()
            jobs = scrape_jobs_for_profile(profile)
            jobs_count = len(jobs)
            logger.info(f"✅ Scraping cycle complete!")
            logger.info(f"📊 Total jobs processed: {jobs_count}")
        except Exception as e:
            logger.error(f"❌ Scraping cycle failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        
        # Calculate cycle time
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        logger.info(f"⏱️  Cycle took {cycle_duration:.1f} seconds")
        logger.info("=" * 60)
        logger.info("✅ CYCLE SUCCESSFUL - Ready for next execution")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Critical error in cloud_run: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main entry point"""
    success = run_one_cycle()
    
    # Exit with proper code for cloud platform monitoring
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
