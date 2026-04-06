"""
Internshala HTML Scraper - Real Implementation (Updated April 5, 2026)
Scrapes internship opportunities from Internshala using HTML parsing
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InternshalaScaper:
    """Real Internshala HTML scraper (API deprecated, using website HTML)."""
    
    BASE_URL = "https://internshala.com"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(InternshalaScaper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://internshala.com/',
        }
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape internship opportunities from Internshala browse page."""
        logger.info("🔍 Scraping Internshala internships...")
        
        jobs = []
        
        try:
            # Fetch main internships page
            url = f"{InternshalaScaper.BASE_URL}/internships/"
            
            time.sleep(random.uniform(0.5, 1.5))
            response = requests.get(url, headers=InternshalaScaper.get_headers(), timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all internship items
                internships = soup.find_all('div', class_='individual_internship')
                logger.info(f"📊 Found {len(internships)} internships on page")
                
                for internship_div in internships[:15]:  # Get up to 15
                    try:
                        # Extract title
                        title_a = internship_div.find('a', class_='job-title-href')
                        title = title_a.text.strip() if title_a else 'Internship Position'
                        
                        # Extract company
                        company_p = internship_div.find('p', class_='company-name')
                        company = company_p.text.strip() if company_p else 'Unknown'
                        
                        # Extract location
                        loc_div = internship_div.find('div', class_='locations')
                        location = 'India'
                        if loc_div and loc_div.find('a'):
                            location = loc_div.find('a').text.strip()
                        
                        # Extract duration
                        dur_span = internship_div.find('span', class_='duration')
                        duration = dur_span.text.strip() if dur_span else 'Not specified'
                        
                        # Extract stipend
                        stip_div = internship_div.find('div', class_='stipend')
                        stipend = stip_div.text.strip() if stip_div else 'Not disclosed'
                        
                        # Extract skills
                        skills_div = internship_div.find('div', class_='skills')
                        skills = skills_div.text.strip() if skills_div else ''
                        
                        # Extract link
                        link = title_a.get('href', '') if title_a else ''
                        if link and not link.startswith('http'):
                            link = f"{InternshalaScaper.BASE_URL}{link}"
                        elif not link:
                            link = internship_div.get('data-href', '')
                            if link and not link.startswith('http'):
                                link = f"{InternshalaScaper.BASE_URL}{link}"
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': location,
                            'description': f'Duration: {duration}\nSkills: {skills}',
                            'requirements': skills,
                            'experience': '0-1 years',
                            'salary_text': stipend,
                            'salary_min': 0,
                            'salary_max': 0,
                            'job_type': 'Internship',
                            'link': link,
                            'platform': 'Internshala',
                            'source': 'Internshala',
                            'posted_date': '',
                            'ats_score': 0,
                            'keywords_matched': []
                        }
                        
                        if link and title != 'Internship Position':
                            jobs.append(job)
                        
                    except Exception as e:
                        logger.debug(f"Error parsing internship: {e}")
                        continue
                
                if jobs:
                    logger.info(f"✅ Found {len(jobs)} internships from Internshala")
            
            else:
                logger.warning(f"Internshala returned status {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ Internshala scraper error: {e}")
        
        return jobs


def scrape_internshala_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper function for compatibility."""
    return InternshalaScaper.scrape(profile)
