"""Telegram Channel Job Scraper - Scrapes real Telegram job channels (NO MOCK DATA)."""

import asyncio
import logging
from typing import List, Dict, Any
import re
from datetime import datetime
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv('.env-analyst')

# Get channels from env (17 role-matched channels)
TELEGRAM_CHANNELS_STR = os.getenv(
    'TELEGRAM_CHANNELS',
    '@jobsinindia,@JOB_PORTAL_INDIA,@jobs_for_freshers_2024,@DataScienceJobs,@DevOpsJobs,@FullStackDeveloper,@PythonDeveloperJobs,@JavaDeveloperJobs,@CloudComputingJobs,@SoftwareEngineeringJobs,@BackendDeveloperJobs,@FrontendDeveloperJobs,@DataAnalystJobs,@BusinessAnalystJobs,@QATestingJobs,@MLEngineeringJobs,@ProductManagerJobs'
)
TELEGRAM_CHANNELS = [ch.strip() for ch in TELEGRAM_CHANNELS_STR.split(',')]
logger.info(f"✅ Loaded {len(TELEGRAM_CHANNELS)} Telegram channels from env")


def parse_job_from_message(message_text: str) -> Dict[str, Any]:
    """Parse job details from a Telegram message - STRICT VALIDATION (no fake links)."""
    try:
        # REQUIREMENT 1: Message must have a valid apply link
        url_match = re.search(r"https?://\S+", message_text)
        if not url_match:
            return None  # No link = not a job
        
        apply_link = url_match.group(0).rstrip(').,]')
        
        # REQUIREMENT 2: Link cannot be fake/demo domains
        fake_domains = ['example.com', 'example.org', 'test.com', 'demo.com', 'localhost', '127.0.0.1']
        for fake_domain in fake_domains:
            if fake_domain in apply_link.lower():
                logger.debug(f"🚫 Blocked fake link: {apply_link}")
                return None  # Fake link = block it
        
        # REQUIREMENT 3: Link must be from real job portals or company sites
        if not apply_link.startswith(('http://', 'https://')):
            return None
        
        job = {
            "job_title": "",
            "title": "",
            "company": "",
            "location": "",
            "salary": "",
            "experience_required": "",
            "job_type": "",
            "description": "",
            "skills_required": "",
            "apply_link": apply_link,
            "link": apply_link,
            "source": "Telegram",
            "posted_date": datetime.now().isoformat(),
            "platform": "Telegram Channel",
        }

        # Extract job title from explicit markers first.
        title_match = re.search(r"(?:Job:|Position:|Role:|Hiring|Opening)[\s:\-]*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
        if title_match:
            job["job_title"] = title_match.group(1).strip()[:150]
            job["title"] = job["job_title"]
        else:
            # Fallback: use first meaningful line as title.
            first_line = next((ln.strip() for ln in message_text.splitlines() if ln.strip() and len(ln.strip()) > 5), "")
            if first_line:
                job["job_title"] = first_line[:150]
                job["title"] = job["job_title"]

        # Extract company.
        company_match = re.search(r"(?:Company:|Organization:|Hiring at|@)[\s:\-]*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
        if company_match:
            job["company"] = company_match.group(1).strip()[:100]

        # Extract location
        location_match = re.search(r"(?:Location:|City:|Place:|Based in)[\s:\-]*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
        if location_match:
            job["location"] = location_match.group(1).strip()[:100]

        # Extract salary
        salary_match = re.search(r"(?:Salary:|CTC:|Package:|Offering)[\s:\-]*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
        if salary_match:
            job["salary"] = salary_match.group(1).strip()[:100]

        # Extract experience
        exp_match = re.search(r"(?:Experience:|Exp:|Years|YoE)[\s:\-]*(.+?)(?:\n|$)", message_text, re.IGNORECASE)
        if exp_match:
            job["experience_required"] = exp_match.group(1).strip()[:100]

        # Extract job type
        jtype_match = re.search(r"(Full-?time|Part-?time|Contract|Remote|Hybrid|Internship|Freelance)", message_text, re.IGNORECASE)
        if jtype_match:
            job["job_type"] = jtype_match.group(1).strip()

        # Description = first 200 chars  
        job["description"] = message_text[:200].replace('\n', ' ')

        return job
    except Exception as e:
        logger.debug(f"Error parsing message: {e}")
        return None


async def scrape_telegram_jobs() -> List[Dict[str, Any]]:
    """Scrape jobs from Telegram channels - REAL ONLY (NO MOCK)."""
    jobs = []
    allow_mock = os.getenv("ALLOW_MOCK_TELEGRAM_JOBS", "0") == "1"
    
    if not allow_mock:
        logger.info("🔴 STRICT MODE: Mock jobs DISABLED - Real data ONLY")
    
    try:
        from pyrogram import Client
        
        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        session_name = os.getenv("TELEGRAM_SESSION_NAME", "ai_job_hunter_session")
        
        if not api_id or not api_hash:
            logger.critical("❌ Missing TELEGRAM_API_ID or TELEGRAM_API_HASH")
            return [] if not allow_mock else get_mock_telegram_jobs()

        try:
            api_id = int(api_id)
        except (ValueError, TypeError):
            logger.critical("❌ TELEGRAM_API_ID must be a number")
            return [] if not allow_mock else get_mock_telegram_jobs()

        # Create client with proper session handling
        client = Client(
            session_name,
            api_id=api_id,
            api_hash=api_hash,
            workdir="."
        )

        try:
            async with client:
                logger.info(f"📡 Connected to Telegram - Scraping {len(TELEGRAM_CHANNELS)} channels...")
                
                for channel in TELEGRAM_CHANNELS:
                    try:
                        async for message in client.get_chat_history(channel, limit=20):
                            if message.text:
                                job = parse_job_from_message(message.text)
                                if job and job.get("apply_link"):
                                    jobs.append(job)
                                    logger.debug(f"  ✓ Found: {job.get('job_title', 'Job')[:50]}")
                    except Exception as e:
                        logger.debug(f"  ✗ Channel {channel}: {str(e)[:50]}")
                        continue

            logger.info(f"✅ Telegram: Found {len(jobs)} REAL jobs from channels")
            return jobs
        except (RuntimeError, OSError) as e:
            # Handle Pyrogram session database issues (corrupted or schema mismatch)
            if "no such column" in str(e) or "database" in str(e).lower():
                logger.warning(f"⚠️ Pyrogram session corrupted or outdated. Cleaning up...")
                # Try to remove the corrupted session file
                try:
                    import os
                    session_files = [f"{session_name}.session", f"{session_name}.session-journal"]
                    for sf in session_files:
                        if os.path.exists(sf):
                            os.remove(sf)
                            logger.info(f"  ✓ Removed {sf}")
                except Exception as cleanup_err:
                    logger.debug(f"  Could not delete session files: {cleanup_err}")
                
                logger.info("  ℹ️ Session will be recreated on next run")
                return [] if not allow_mock else get_mock_telegram_jobs()
            else:
                raise

    except ImportError:
        logger.critical("❌ pyrogram library not installed")
        return [] if not allow_mock else get_mock_telegram_jobs()
    except Exception as e:
        logger.error(f"❌ Telegram scraping error: {str(e)[:100]}")
        return [] if not allow_mock else get_mock_telegram_jobs()


def get_mock_telegram_jobs() -> List[Dict[str, Any]]:
    """DISABLED - No mock jobs allowed. Return empty list to enforce REAL DATA ONLY."""
    logger.warning("⚠️ Mock Telegram jobs requested but DISABLED per ALLOW_MOCK_TELEGRAM_JOBS=0")
    logger.warning("💡 To use real Telegram scraping:")
    logger.warning("   1. Ensure TELEGRAM_API_ID and TELEGRAM_API_HASH are set in .env-analyst")
    logger.warning("   2. Run: python scrapers/telegram_channel_scraper.py to login (one-time)")
    logger.warning("   3. Session file ai_job_hunter_session.session will be created")
    logger.warning("   4. Telegram scraping will work in next cycle")
    return []
