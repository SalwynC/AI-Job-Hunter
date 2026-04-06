"""
Nuvoco / NCS India Jobs Portal Scraper
National Careers Service (NCS) India jobs.
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


class NuvocoScraper:
    """Nuvoco/NCS India job scraper."""
    
    BASE_URL = "https://www.ncsindiaonline.org"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(NuvocoScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    @staticmethod
    def scrape_job_listings() -> List[Dict[str, Any]]:
        """Scrape Nuvoco job listings."""
        jobs = []
        
        try:
            # Try main jobs page
            response = requests.get(
                f"{NuvocoScraper.BASE_URL}/jobs",
                headers=NuvocoScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings (may vary by site structure)
                job_containers = soup.find_all('div', class_='job-listing')
                
                if not job_containers:
                    job_containers = soup.find_all('article')
                
                if not job_containers:
                    job_containers = soup.find_all('li', {'data-id': True})
                
                for container in job_containers[:15]:
                    try:
                        # Extract job title
                        title_elem = container.find(['h2', 'h3', 'a'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            
                            # Extract link
                            link_elem = container.find('a', href=True)
                            link = link_elem.get('href', '')
                            if link and not link.startswith('http'):
                                link = NuvocoScraper.BASE_URL + link
                            
                            # Extract company/organization
                            company_elem = container.find('p', class_=['company', 'organization'])
                            company = company_elem.get_text(strip=True) if company_elem else 'Nuvoco'
                            
                            # Extract location
                            location_elem = container.find(['span', 'p'], class_='location')
                            location = location_elem.get_text(strip=True) if location_elem else 'India'
                            
                            # Extract experience
                            exp_elem = container.find('span', class_='experience')
                            experience = exp_elem.get_text(strip=True) if exp_elem else ''
                            
                            if title and link:
                                jobs.append({
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'experience': experience,
                                    'link': link,
                                    'source': 'Nuvoco',
                                })
                    except Exception as e:
                        logger.debug(f"Error parsing Nuvoco job: {e}")
                
                time.sleep(random.uniform(2, 3))
        
        except Exception as e:
            logger.debug(f"Nuvoco scraper error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_category(category: str) -> List[Dict[str, Any]]:
        """Scrape jobs by category."""
        jobs = []
        
        try:
            # Try category-based scraping
            url = f"{NuvocoScraper.BASE_URL}/jobs?category={quote(category)}"
            response = requests.get(
                url,
                headers=NuvocoScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_containers = soup.find_all('div', class_='job-item')
                if not job_containers:
                    job_containers = soup.find_all('article')
                
                for container in job_containers[:10]:
                    try:
                        title_elem = container.find(['h2', 'h3'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        link_elem = container.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = NuvocoScraper.BASE_URL + link
                        
                        if title and link:
                            jobs.append({
                                'title': title,
                                'category': category,
                                'link': link,
                                'source': 'Nuvoco',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing category job: {e}")
                
                time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            logger.debug(f"Nuvoco category scrape error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping Nuvoco/NCS India jobs...")
        
        jobs = []
        
        # Scrape main listings
        jobs.extend(cls.scrape_job_listings())
        
        # Try scraping by categories
        categories = ['IT', 'Engineering', 'Administrative', 'Healthcare']
        for category in categories:
            jobs.extend(cls.scrape_category(category))
        
        # Deduplicate by link
        seen = set()
        unique_jobs = []
        for job in jobs:
            link = job.get('link', '')
            if link and link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 Nuvoco: {len(unique_jobs)} jobs")
        return unique_jobs


def scrape_nuvoco_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return NuvocoScraper.scrape(profile)
