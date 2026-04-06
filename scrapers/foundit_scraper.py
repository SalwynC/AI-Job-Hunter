"""
Foundit.in Scraper (formerly Monster India)
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


class FounditScraper:
    """Foundit.in job scraper."""
    
    BASE_URL = "https://www.foundit.in"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(FounditScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://www.foundit.in/'
        }
    
    @staticmethod
    def scrape_search_results(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape Foundit search results page."""
        jobs = []
        
        try:
            keywords = profile.get('keywords', ['software engineer', 'data analyst'])[:2]
            
            for keyword in keywords:
                try:
                    search_url = f"{FounditScraper.BASE_URL}/srp?q={quote(keyword)}&l=India"
                    
                    response = requests.get(
                        search_url,
                        headers=FounditScraper.get_headers(),
                        timeout=12
                    )
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Find job cards (Foundit uses specific class names)
                        job_cards = soup.find_all('div', class_='job-card')
                        
                        if not job_cards:
                            # Try alternative selectors
                            job_cards = soup.find_all('article', class_='job-item')
                        
                        if not job_cards:
                            job_cards = soup.find_all('li', {'data-job-id': True})
                        
                        for card in job_cards[:10]:
                            try:
                                title_elem = card.find(['h2', 'h3', 'a'])
                                title = title_elem.get_text(strip=True) if title_elem else 'Job'
                                
                                link_elem = card.find('a', href=True)
                                link = link_elem.get('href', '') if link_elem else ''
                                if link and not link.startswith('http'):
                                    link = FounditScraper.BASE_URL + link
                                
                                company_elem = card.find('p', class_='company-name')
                                company = company_elem.get_text(strip=True) if company_elem else 'Company'
                                
                                location_elem = card.find('span', class_='location')
                                location = location_elem.get_text(strip=True) if location_elem else 'India'
                                
                                if title and link:
                                    jobs.append({
                                        'title': title,
                                        'company': company,
                                        'location': location,
                                        'link': link,
                                        'source': 'Foundit',
                                    })
                            except Exception as e:
                                logger.debug(f"Error parsing Foundit job card: {e}")
                    
                    time.sleep(random.uniform(2, 4))
                
                except Exception as e:
                    logger.debug(f"Foundit search failed for '{keyword}': {e}")
        
        except Exception as e:
            logger.error(f"Foundit scraper error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping Foundit.in jobs...")
        
        jobs = cls.scrape_search_results(profile)
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in jobs:
            link = job.get('link', '')
            if link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 Foundit: {len(unique_jobs)} jobs")
        return unique_jobs


def scrape_foundit_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return FounditScraper.scrape(profile)
