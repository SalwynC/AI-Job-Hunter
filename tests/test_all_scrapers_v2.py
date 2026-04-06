#!/usr/bin/env python3
"""
🚀 QUICK SCRAPER TEST - Validate all working scrapers in 2 minutes
Run: python3 test_all_scrapers_v2.py
"""

import time
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def test_naukri_v2():
    """Test Naukri API V2."""
    logger.info(f"{BLUE}Testing Naukri API V2...{RESET}")
    
    try:
        from scrapers.naukri_scraper_v2_api import scrape_naukri_jobs
        
        profile = {
            'queries': {'naukri': ['python developer', 'data analyst']},
            'experience_level': [1, 2, 3]
        }
        
        start = time.time()
        jobs = scrape_naukri_jobs(profile)
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ Naukri V2: {len(jobs)} jobs found ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  Naukri V2: 0 jobs (API may be blocked){RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ Naukri V2: {str(e)[:60]}{RESET}")
        return False, 0


def test_indeed_rss():
    """Test Indeed RSS scraper."""
    logger.info(f"{BLUE}Testing Indeed RSS...{RESET}")
    
    try:
        from scrapers.free_portals_scraper import IndeedFreeAPI
        
        profile = {
            'queries': {'indeed': ['python developer', 'data analyst']}
        }
        
        start = time.time()
        jobs = IndeedFreeAPI.scrape(profile)
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ Indeed RSS: {len(jobs)} jobs ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  Indeed RSS: 0 jobs{RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ Indeed RSS: {str(e)[:60]}{RESET}")
        return False, 0


def test_internshala():
    """Test Internshala scraper."""
    logger.info(f"{BLUE}Testing Internshala...{RESET}")
    
    try:
        from scrapers.free_portals_scraper import InternshalaFreeAPI
        
        profile = {
            'queries': {'internshala': ['data science internship']}
        }
        
        start = time.time()
        jobs = InternshalaFreeAPI.scrape(profile)
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ Internshala: {len(jobs)} jobs ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  Internshala: 0 jobs{RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ Internshala: {str(e)[:60]}{RESET}")
        return False, 0


def test_remoteok():
    """Test RemoteOK scraper."""
    logger.info(f"{BLUE}Testing RemoteOK...{RESET}")
    
    try:
        from scrapers.free_portals_scraper import RemoteOKFree
        
        profile = {}
        
        start = time.time()
        jobs = RemoteOKFree.scrape(profile)
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ RemoteOK: {len(jobs)} India jobs ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  RemoteOK: 0 jobs{RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ RemoteOK: {str(e)[:60]}{RESET}")
        return False, 0


def test_telegram():
    """Test Telegram scraper."""
    logger.info(f"{BLUE}Testing Telegram scraper...{RESET}")
    
    try:
        from scrapers.telegram_scraper_improved import scrape_telegram_jobs_simple
        
        start = time.time()
        jobs = scrape_telegram_jobs_simple()
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ Telegram: {len(jobs)} jobs ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  Telegram: 0 jobs (requires setup or active channels){RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ Telegram: {str(e)[:60]}{RESET}")
        return False, 0


def test_common_scraper():
    """Test the integrated common scraper."""
    logger.info(f"{BLUE}Testing integrated scraper (scrapers.common)...{RESET}")
    
    try:
        from scrapers.common import scrape_jobs_for_profile
        
        profile = {
            'role_key': 'data_analyst',
            'queries': {
                'naukri': ['data analyst'],
                'free_portals': ['data analyst'],
            },
            'preferred_locations': ['India'],
            'experience_level': [1, 2, 3]
        }
        
        start = time.time()
        jobs = scrape_jobs_for_profile(profile)
        duration = time.time() - start
        
        if jobs:
            logger.info(f"{GREEN}✅ Integrated: {len(jobs)} total jobs ({duration:.1f}s){RESET}")
            return True, len(jobs)
        else:
            logger.info(f"{YELLOW}⚠️  Integrated: 0 jobs{RESET}")
            return False, 0
    except Exception as e:
        logger.error(f"{RED}❌ Integrated: {str(e)[:80]}{RESET}")
        import traceback
        logger.debug(traceback.format_exc())
        return False, 0


def main():
    """Run all tests."""
    logger.info(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    logger.info(f"{BOLD}{BLUE}🚀 SCRAPER VALIDATION TEST{RESET}")
    logger.info(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    # Check imports
    logger.info(f"{BLUE}Step 1: Checking dependencies...{RESET}")
    try:
        import requests
        import bs4
        logger.info(f"{GREEN}✅ requests, beautifulsoup4 available{RESET}\n")
    except ImportError as e:
        logger.error(f"{RED}❌ Missing: {e}{RESET}")
        logger.error("Install with: pip install requests beautifulsoup4")
        return False
    
    # Run tests
    logger.info(f"{BLUE}Step 2: Testing individual scrapers...{RESET}\n")
    
    results = {
        'Naukri V2 API': test_naukri_v2(),
        'Indeed RSS': test_indeed_rss(),
        'Internshala': test_internshala(),
        'RemoteOK': test_remoteok(),
        'Telegram': test_telegram(),
    }
    
    # Test integrated scraper
    logger.info()
    logger.info(f"{BLUE}Step 3: Testing integrated scraper...{RESET}\n")
    integrated_ok, integrated_count = test_common_scraper()
    
    # Summary
    logger.info(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    logger.info(f"{BOLD}{BLUE}📊 TEST SUMMARY{RESET}")
    logger.info(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for ok, _ in results.values() if ok)
    total = len(results)
    total_jobs = sum(count for _, count in results.values())
    
    logger.info(f"{BLUE}Individual Scrapers:{RESET} {passed}/{total} working")
    logger.info(f"{BLUE}Total Jobs Found:{RESET} {total_jobs}")
    logger.info(f"{BLUE}Integrated Scraper:{RESET} {'✅ Working' if integrated_ok else '⚠️  Needs config'}")
    
    if total_jobs > 0 or integrated_count > 0:
        logger.info(f"\n{GREEN}{BOLD}✅ SUCCESS! System is ready to use.{RESET}")
        logger.info(f"{GREEN}Run: python3 main.py{RESET}\n")
        return True
    else:
        logger.info(f"\n{YELLOW}{BOLD}⚠️  WARNING: All sources returned 0 jobs{RESET}")
        logger.info(f"{YELLOW}This may indicate:{RESET}")
        logger.info(f"  1. Network connectivity issues")
        logger.info(f"  2. All APIs temporarily blocked (try again later)")
        logger.info(f"  3. Incorrect profile configuration")
        logger.info(f"\n{YELLOW}Try: python3 main.py (will generate synthetic data as fallback){RESET}\n")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
