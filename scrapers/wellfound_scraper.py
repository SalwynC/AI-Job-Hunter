"""
Wellfound.com Scraper (formerly AngelList)
Startup jobs and early-stage company positions.
Real scraping. No mock data.
"""

import requests
import logging
import time
import random
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from urllib.parse import quote

logger = logging.getLogger(__name__)


class WellfoundScraper:
    """Wellfound.com job scraper."""
    
    BASE_URL = "https://wellfound.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(WellfoundScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://wellfound.com',
        }
    
    @staticmethod
    def scrape_jobs_page() -> List[Dict[str, Any]]:
        """Scrape Wellfound jobs page."""
        jobs = []
        
        try:
            response = requests.get(
                f"{WellfoundScraper.BASE_URL}/jobs",
                headers=WellfoundScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Wellfound job cards
                job_cards = soup.find_all('div', class_=['job-card', 'job-item', 'job'])
                
                for card in job_cards[:15]:
                    try:
                        # Title
                        title_elem = card.find(['h2', 'h3', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        # Link
                        link_elem = card.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = WellfoundScraper.BASE_URL + link
                        
                        # Company (Startup name)
                        company_elem = card.find(['span', 'p'], class_=['company', 'startup-name'])
                        if not company_elem:
                            company_elem = card.find(['span', 'p'])
                        company = company_elem.get_text(strip=True) if company_elem else 'Startup'
                        
                        # Location (many are remote)
                        location_elem = card.find(['span', 'p'], class_='location')
                        location = location_elem.get_text(strip=True) if location_elem else 'Remote/India'
                        
                        # Salary if available
                        salary_elem = card.find(['span', 'p'], class_='salary')
                        salary = salary_elem.get_text(strip=True) if salary_elem else ''
                        
                        if title and link:
                            jobs.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'salary': salary,
                                'link': link,
                                'source': 'Wellfound',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing Wellfound job: {e}")
                
                time.sleep(random.uniform(2, 3))
        
        except Exception as e:
            logger.debug(f"Wellfound page error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_by_role(role: str) -> List[Dict[str, Any]]:
        """Scrape jobs by role/keyword."""
        jobs = []
        
        try:
            search_url = f"{WellfoundScraper.BASE_URL}/jobs?q={quote(role)}"
            response = requests.get(
                search_url,
                headers=WellfoundScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_cards = soup.find_all('div', class_=['job-card', 'job-item'])
                
                for card in job_cards[:10]:
                    try:
                        title_elem = card.find(['h2', 'h3', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        link_elem = card.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = WellfoundScraper.BASE_URL + link
                        
                        if title and link:
                            jobs.append({
                                'title': title,
                                'link': link,
                                'source': 'Wellfound',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing role search result: {e}")
                
                time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            logger.debug(f"Wellfound role search error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping Wellfound jobs...")
        
        all_jobs = []
        
        # Get main jobs page
        all_jobs.extend(cls.scrape_jobs_page())
        
        # Try searching by common roles
        roles = ['Software Engineer', 'Data Analyst', 'Product Manager']
        for role in roles:
            all_jobs.extend(cls.scrape_by_role(role))
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            link = job.get('link', '')
            if link and link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 Wellfound: {len(unique_jobs)} jobs")
        return unique_jobs


def scrape_wellfound_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return WellfoundScraper.scrape(profile)
