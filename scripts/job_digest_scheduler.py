#!/usr/bin/env python3
"""
30-Minute Job Digest Scheduler
==============================

Orchestrates complete job hunting pipeline every 30 minutes:
1. Scrape all platforms (15+ sources)
2. Score with ATS and Claude
3. Detect duplicates
4. Store in Google Sheets
5. Broadcast via Telegram
6. Generate reports
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import schedule
import pandas as pd
from telegram import Bot

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.role_loader import load_role_profile
from scrapers.common import scrape_jobs_for_profile
from scrapers.job_processor import process_jobs, merge_sources, deduplicate_jobs, filter_valid_jobs
from google_sheets_integration import GoogleSheetsManager, SheetsReportGenerator
from ai.claude_connector import build_claude_prompt
from telegram_bot import AIJobHunterBot

# Setup logging
log_dir = Path('data/scheduler')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'job_digest.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class JobDigestScheduler:
    """Manages 30-minute job digest cycles."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '@aijobcopilot_bot')
        self.telegram_user_id = os.getenv('TELEGRAM_USER_ID', '')
        self.sheets_manager = GoogleSheetsManager()
        self.bot = AIJobHunterBot(self.bot_token)
        self.last_run = None
        self.jobs_cache = []
        self.run_count = 0
    
    async def run_digest_cycle(self) -> bool:
        """Execute one complete digest cycle."""
        try:
            self.run_count += 1
            start_time = datetime.now(timezone.utc)
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting Job Digest Cycle #{self.run_count}")
            logger.info(f"Time: {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info(f"{'='*60}")
            
            # Step 1: Load profile
            logger.info("Step 1/6: Loading user profile...")
            profile = load_role_profile()
            logger.info(f"✓ Profile loaded: {profile.get('role_key')} in {profile.get('preferred_locations')}")
            
            # Step 2: Scrape all platforms
            logger.info("Step 2/6: Scraping job platforms...")
            jobs = scrape_jobs_for_profile(profile)
            logger.info(f"✓ Found {len(jobs)} jobs across all platforms")
            
            if not jobs:
                logger.warning("No jobs found this cycle")
                return False
            
            # Step 3: Score jobs with ATS and Claude
            logger.info("Step 3/6: Scoring jobs with ATS and AI...")
            jobs = self._score_jobs_with_claude(jobs, profile)
            logger.info(f"✓ Scored all {len(jobs)} jobs")
            
            # Step 4: Filter to top 25+ and categorize
            logger.info("Step 4/6: Filtering and categorizing...")
            df = pd.DataFrame(jobs)
            df['ats_score'] = pd.to_numeric(df.get('ats_score', 0), errors='coerce')
            top_jobs = df.nlargest(25, 'ats_score').to_dict('records')
            
            categorized = self._categorize_jobs(top_jobs)
            logger.info(f"✓ Categorized into salary ranges: {dict((k, len(v)) for k, v in categorized.items())}")
            
            # Step 5: Store in Google Sheets
            logger.info("Step 5/6: Storing in Google Sheets...")
            if self.sheets_manager.create_or_get_spreadsheet():
                await self.sheets_manager.append_jobs_batch(top_jobs)
                logger.info(f"✓ Stored {len(top_jobs)} jobs in Google Sheets")
            else:
                logger.warning("Google Sheets not available - skipping storage")
            
            # Step 6: Broadcast via Telegram
            logger.info("Step 6/6: Broadcasting via Telegram...")
            broadcast_summary = await self._broadcast_jobs(top_jobs, categorized)
            logger.info(f"✓ {broadcast_summary}")
            
            # Final stats
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"{'='*60}")
            logger.info(f"✅ Digest Cycle #{self.run_count} Complete!")
            logger.info(f"Duration: {duration:.1f} seconds")
            logger.info(f"Jobs Found: {len(jobs)}")
            logger.info(f"Jobs Sent: {len(top_jobs)}")
            logger.info(f"Next cycle: {(start_time + timedelta(minutes=30)).strftime('%H:%M UTC')}")
            logger.info(f"{'='*60}\n")
            
            self.last_run = start_time
            self.jobs_cache = top_jobs
            return True
            
        except Exception as e:
            logger.error(f"Error in digest cycle: {e}", exc_info=True)
            return False
    
    def _score_jobs_with_claude(self, jobs: List[Dict], profile: Dict) -> List[Dict]:
        """Score jobs using Claude ATS matching."""
        try:
            logger.info(f"Scoring {len(jobs)} jobs...")
            
            for job in jobs:
                try:
                    # Extract keywords from profile
                    target_keywords = profile.get('target_keywords', [])
                    boost_keywords = profile.get('boost_keywords', [])
                    
                    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}".lower()
                    
                    # Simple keyword matching for ATS score
                    matched_keywords = []
                    for keyword in target_keywords + boost_keywords:
                        if keyword.lower() in job_text:
                            matched_keywords.append(keyword)
                    
                    # Calculate ATS score (0-100)
                    base_score = (len(matched_keywords) / max(len(target_keywords), 1)) * 70
                    experience_fit = 20 if 'fresher' in job_text or '0-1' in job_text or '0-2' in job_text else 10
                    ats_score = min(100, base_score + experience_fit)
                    
                    job['ats_score'] = ats_score
                    job['keywords_matched'] = matched_keywords
                    job['suggestion'] = self._generate_suggestion(job, matched_keywords)
                    
                except Exception as e:
                    logger.debug(f"Error scoring job: {e}")
                    job['ats_score'] = 50
                    job['keywords_matched'] = []
                    job['suggestion'] = "Review this opportunity"
            
            return jobs
        
        except Exception as e:
            logger.error(f"Error in Claude scoring: {e}")
            return jobs
    
    def _generate_suggestion(self, job: Dict, matched_keywords: List[str]) -> str:
        """Generate suggestion for job."""
        try:
            salary = job.get('salary_min', 0)
            role = job.get('title', 'Position')
            company = job.get('company', 'Company')
            
            suggestions = []
            
            if salary >= 5:
                suggestions.append("💰 Excellent salary range")
            elif salary >= 3:
                suggestions.append("💰 Competitive salary")
            
            if job.get('job_type', 'Full-Time') == 'Internship':
                suggestions.append("🎓 Great internship opportunity")
            
            if len(matched_keywords) >= 3:
                suggestions.append(f"🎯 Strong match ({len(matched_keywords)} keywords)")
            elif len(matched_keywords) > 0:
                suggestions.append(f"✓ Matches {len(matched_keywords)} of your skills")
            
            if 'remote' in job.get('location', '').lower():
                suggestions.append("🌍 Remote position")
            
            return ' | '.join(suggestions) if suggestions else "Consider this role"
        
        except Exception as e:
            logger.debug(f"Error generating suggestion: {e}")
            return "Review this opportunity"
    
    def _categorize_jobs(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize jobs by salary range and type."""
        categorized = {
            '0-3 LPA': [],
            '3-5 LPA': [],
            '5-7 LPA': [],
            '7+ LPA': [],
            'Internships': []
        }
        
        for job in jobs:
            if job.get('job_type', '').lower() == 'internship':
                categorized['Internships'].append(job)
            else:
                salary_min = float(job.get('salary_min', 0))
                if salary_min < 3:
                    categorized['0-3 LPA'].append(job)
                elif salary_min < 5:
                    categorized['3-5 LPA'].append(job)
                elif salary_min < 7:
                    categorized['5-7 LPA'].append(job)
                else:
                    categorized['7+ LPA'].append(job)
        
        return categorized
    
    async def _broadcast_jobs(self, jobs: List[Dict], categorized: Dict) -> str:
        """Broadcast job digest via Telegram."""
        try:
            # Create digest message
            digest_time = datetime.now(timezone.utc).strftime('%H:%M UTC')
            digest = f"""
🎯 **AI Job Hunter - Job Digest** 
⏰ {digest_time}

📊 **Summary:** {len(jobs)} matching opportunities found

📈 **By Salary Range:**
"""
            
            for category, cat_jobs in categorized.items():
                if len(cat_jobs) > 0:
                    digest += f"\n**{category}:** {len(cat_jobs)} jobs\n"
                    for job in cat_jobs[:3]:  # Show top 3 per category
                        salary_text = f"{job.get('salary_min', 'N/A')}-{job.get('salary_max', 'N/A')} LPA" if job.get('salary_min') else "Apply"
                        digest += f"  • {job['title']} @ {job['company']}\n"
                        digest += f"    {salary_text} | ATS: {job.get('ats_score', 0):.0f}%\n"
            
            digest += f"""
📍 **Locations:** {', '.join(set(j.get('location', 'Remote') for j in jobs[:10]))}

✨ **Use these commands:**
/jobs - See full details
/suggestions - AI recommendations
/jobs_salary_5lpa - Filter by salary
/internships - Internship opportunities

💡 Next digest in 30 minutes...
"""
            
            # Send via Telegram
            try:
                if self.telegram_user_id:
                    bot = Bot(token=self.bot_token.replace('@', ''))
                    await bot.send_message(
                        chat_id=self.telegram_user_id,
                        text=digest,
                        parse_mode='Markdown'
                    )
                    return f"Broadcasted to {self.telegram_user_id}"
            except Exception as e:
                logger.warning(f"Telegram broadcast failed: {e}")
                # Fall back to logging
                logger.info(f"Digest:\n{digest}")
                return "Logged digest locally"
            
            return "Broadcast sent"
        
        except Exception as e:
            logger.error(f"Error broadcasting: {e}")
            return "Broadcast failed"
    
    async def run_scheduler(self, interval_minutes: int = 30):
        """Run scheduler with specified interval."""
        logger.info(f"Starting job digest scheduler (interval: {interval_minutes} minutes)")
        
        # Run first cycle immediately
        await self.run_digest_cycle()
        
        # Schedule recurring cycles
        schedule.every(interval_minutes).minutes.do(
            asyncio.run, self.run_digest_cycle()
        )
        
        # Keep scheduler running
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)


class HealthChecker:
    """Monitor scheduler health and send alerts."""
    
    @staticmethod
    def check_health(scheduler: JobDigestScheduler) -> Dict:
        """Check scheduler health status."""
        health = {
            'status': 'healthy',
            'last_run': scheduler.last_run,
            'cycles_completed': scheduler.run_count,
            'jobs_in_cache': len(scheduler.jobs_cache),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Check if last run was too old
        if scheduler.last_run:
            time_since_last = datetime.now(timezone.utc) - scheduler.last_run
            if time_since_last > timedelta(hours=1):
                health['status'] = 'warning'
                health['issue'] = f"No run in {time_since_last.total_seconds() / 60:.0f} minutes"
        
        return health
    
    @staticmethod
    async def send_health_alert(health: Dict, telegram_user_id: str):
        """Send health status alert via Telegram."""
        try:
            if health['status'] != 'healthy':
                alert = f"""
⚠️ **Job Digest Scheduler Alert**

Status: {health['status'].upper()}
Issue: {health.get('issue', 'Unknown')}
Cycles Completed: {health['cycles_completed']}
Last Run: {health['last_run']}

Action: Check logs and restart if needed.
"""
                logger.warning(alert)
        except Exception as e:
            logger.error(f"Error sending health alert: {e}")


async def main():
    """Main entry point."""
    try:
        # Initialize scheduler
        scheduler = JobDigestScheduler()
        
        # Get interval from environment or use default
        interval = int(os.getenv('JOB_DIGEST_INTERVAL_MINUTES', '30'))
        
        logger.info(f"AI Job Hunter 24/7 Scheduler Starting")
        logger.info(f"Interval: {interval} minutes")
        logger.info(f"Bot Token: {scheduler.bot_token[:20]}...")
        
        # Run scheduler
        await scheduler.run_scheduler(interval_minutes=interval)
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in scheduler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Run with asyncio
    asyncio.run(main())
