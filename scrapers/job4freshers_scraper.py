"""
Job4Freshers.co.in Scraper
Internship and entry-level jobs for freshers.
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


class Job4FreshersScraper:
    """Job4Freshers.co.in scraper - freshers jobs."""
    
    BASE_URL = "https://www.job4freshers.co.in"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(Job4FreshersScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    @staticmethod
    def scrape_main_page() -> List[Dict[str, Any]]:
        """Scrape main jobs page."""
        jobs = []
        
        try:
            response = requests.get(
                f"{Job4FreshersScraper.BASE_URL}/walkins",
                headers=Job4FreshersScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_rows = soup.find_all('tr', class_=['job-row', 'job-item'])
                if not job_rows:
                    job_rows = soup.find_all('div', class_=['job-card', 'job'])
                
                for row in job_rows[:15]:
                    try:
                        # Extract title
                        title_elem = row.find(['td', 'span'], class_='title')
                        if not title_elem:
                            title_elem = row.find(['h3', 'h4', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        # Extract company
                        company_elem = row.find(['td', 'span'], class_='company')
                        company = company_elem.get_text(strip=True) if company_elem else 'Company'
                        
                        # Extract link
                        link_elem = row.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = Job4FreshersScraper.BASE_URL + link
                        
                        # Extract location
                        location_elem = row.find(['td', 'span'], class_='location')
                        location = location_elem.get_text(strip=True) if location_elem else 'India'
                        
                        # Extract posted date
                        date_elem = row.find(['td', 'span'], class_='date')
                        posted_date = date_elem.get_text(strip=True) if date_elem else ''
                        
                        if title and link:
                            jobs.append({
                                'title': title,
                                'company': company,
                                'location': location,
                                'posted_date': posted_date,
                                'link': link,
                                'source': 'Job4Freshers',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing Job4Freshers job: {e}")
                
                time.sleep(random.uniform(2, 3))
        
        except Exception as e:
            logger.debug(f"Job4Freshers main page error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_internships() -> List[Dict[str, Any]]:
        """Scrape internship listings."""
        jobs = []
        
        try:
            response = requests.get(
                f"{Job4FreshersScraper.BASE_URL}/internships",
                headers=Job4FreshersScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_items = soup.find_all(['div', 'tr'], class_=['internship', 'job-item'])
                
                for item in job_items[:10]:
                    try:
                        title_elem = item.find(['h3', 'h4', 'a', 'td'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        link_elem = item.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = Job4FreshersScraper.BASE_URL + link
                        
                        if title and link:
                            jobs.append({
                                'title': title + ' (Internship)',
                                'link': link,
                                'source': 'Job4Freshers',
                                'job_type': 'Internship',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing internship: {e}")
                
                time.sleep(random.uniform(2, 3))
        
        except Exception as e:
            logger.debug(f"Job4Freshers internship scrape error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping Job4Freshers jobs...")
        
        all_jobs = []
        
        # Scrape main jobs
        all_jobs.extend(cls.scrape_main_page())
        
        # Scrape internships
        all_jobs.extend(cls.scrape_internships())
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            link = job.get('link', '')
            if link and link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 Job4Freshers: {len(unique_jobs)} jobs")
        return unique_jobs


def scrape_job4freshers_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return Job4FreshersScraper.scrape(profile)
