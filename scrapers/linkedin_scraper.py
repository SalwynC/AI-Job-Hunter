"""
LinkedIn Jobs Scraper - Using Unofficial Approaches
No demo data. Real scraping with fallback strategies.
"""

import requests
import logging
import time
import random
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from urllib.parse import quote

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """LinkedIn job scraper - multiple approaches to avoid blocking."""
    
    BASE_URL = "https://www.linkedin.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    @staticmethod
    def get_headers():
        """Return headers that don't trigger LinkedIn blocking."""
        return {
            'User-Agent': random.choice(LinkedInScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @staticmethod
    def scrape_via_google_search(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape LinkedIn jobs via Google Search operator (site:linkedin.com/jobs)."""
        jobs = []
        
        try:
            keywords = profile.get('keywords', ['software engineer', 'data analyst'])[:2]
            
            for keyword in keywords:
                try:
                    # Google search operator: site:linkedin.com/jobs + keyword + location
                    search_query = f'site:linkedin.com/jobs "{keyword}" India'
                    search_url = f"https://www.google.com/search?q={quote(search_query)}"
                    
                    response = requests.get(
                        search_url,
                        headers=LinkedInScraper.get_headers(),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract job links from search results
                        for link in soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if 'linkedin.com/jobs/view' in href and 'jobs' in href:
                                title = link.get_text(strip=True)
                                if title and len(title) > 5:
                                    jobs.append({
                                        'title': title,
                                        'link': href,
                                        'source': 'LinkedIn (Google)',
                                        'company': 'LinkedIn',
                                        'location': 'India',
                                    })
                    
                    time.sleep(random.uniform(2, 4))
                
                except Exception as e:
                    logger.debug(f"LinkedIn Google search failed for '{keyword}': {e}")
        
        except Exception as e:
            logger.error(f"LinkedIn Google search scraper error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_via_direct_api(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Try direct LinkedIn API endpoint (may be limited)."""
        jobs = []
        
        try:
            keywords = profile.get('keywords', ['software engineer'])[:1]
            
            for keyword in keywords:
                try:
                    # LinkedIn Jobs API endpoint
                    api_url = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting"
                    
                    params = {
                        'keywords': keyword,
                        'location': 'India',
                        'start': 0,
                        'count': 10
                    }
                    
                    response = requests.get(
                        api_url,
                        params=params,
                        headers=LinkedInScraper.get_headers(),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            for job in data.get('elements', []):
                                jobs.append({
                                    'title': job.get('title', 'Job'),
                                    'company': job.get('companyName', 'Company'),
                                    'link': job.get('applyUrl', ''),
                                    'location': 'India',
                                    'source': 'LinkedIn API',
                                })
                        except:
                            logger.debug("LinkedIn API returned non-JSON or different structure")
                    
                    time.sleep(random.uniform(2, 4))
                
                except Exception as e:
                    logger.debug(f"LinkedIn direct API failed for '{keyword}': {e}")
        
        except Exception as e:
            logger.error(f"LinkedIn direct API scraper error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method - try multiple approaches."""
        logger.info("🔍 Scraping LinkedIn jobs...")
        
        all_jobs = []
        
        # Try Google search first
        jobs = cls.scrape_via_google_search(profile)
        all_jobs.extend(jobs)
        logger.info(f"✅ LinkedIn (via Google): Found {len(jobs)} jobs")
        
        # Try direct API
        if len(all_jobs) < 5:
            jobs = cls.scrape_via_direct_api(profile)
            all_jobs.extend(jobs)
            logger.info(f"✅ LinkedIn (via API): Found {len(jobs)} jobs")
        
        # Deduplicate by link
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            link = job.get('link', '')
            if link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 LinkedIn: {len(unique_jobs)} total unique jobs")
        return unique_jobs


def scrape_linkedin_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return LinkedInScraper.scrape(profile)
