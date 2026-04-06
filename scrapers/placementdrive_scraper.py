"""
PlacementDrive.in Scraper
Campus recruitment and placement drives.
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


class PlacementDriveScraper:
    """PlacementDrive.in scraper - campus placements."""
    
    BASE_URL = "https://www.placementdrive.in"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    @staticmethod
    def get_headers():
        return {
            'User-Agent': random.choice(PlacementDriveScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://www.placementdrive.in',
        }
    
    @staticmethod
    def scrape_drives() -> List[Dict[str, Any]]:
        """Scrape active placement drives."""
        jobs = []
        
        try:
            response = requests.get(
                f"{PlacementDriveScraper.BASE_URL}/",
                headers=PlacementDriveScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find drive cards
                drive_cards = soup.find_all('div', class_=['drive-card', 'company-drive', 'placement-drive'])
                
                if not drive_cards:
                    drive_cards = soup.find_all(['article', 'li'], {'data-drive': True})
                
                for card in drive_cards[:15]:
                    try:
                        # Company name / Drive title
                        title_elem = card.find(['h2', 'h3', 'h4', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else 'Placement Drive'
                        
                        # Link to drive details
                        link_elem = card.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = PlacementDriveScraper.BASE_URL + link
                        
                        # Position/Roll
                        position_elem = card.find(['span', 'p'], class_='position')
                        position = position_elem.get_text(strip=True) if position_elem else 'Various'
                        
                        # Location
                        location_elem = card.find(['span', 'p'], class_='location')
                        location = location_elem.get_text(strip=True) if location_elem else 'India'
                        
                        # Drive date
                        date_elem = card.find(['span', 'p'], class_=['date', 'drive-date'])
                        drive_date = date_elem.get_text(strip=True) if date_elem else ''
                        
                        # Eligibility criteria (if shown)
                        criteria_elem = card.find(['span', 'p'], class_='criteria')
                        criteria = criteria_elem.get_text(strip=True) if criteria_elem else ''
                        
                        if title and link:
                            jobs.append({
                                'title': f"{title} - {position}",
                                'company': title,
                                'location': location,
                                'drive_date': drive_date,
                                'position': position,
                                'criteria': criteria,
                                'link': link,
                                'source': 'PlacementDrive',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing drive card: {e}")
                
                time.sleep(random.uniform(2, 3))
        
        except Exception as e:
            logger.debug(f"PlacementDrive scraping error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_by_company(company: str) -> List[Dict[str, Any]]:
        """Scrape drives by specific company."""
        jobs = []
        
        try:
            search_url = f"{PlacementDriveScraper.BASE_URL}/search?company={quote(company)}"
            response = requests.get(
                search_url,
                headers=PlacementDriveScraper.get_headers(),
                timeout=12
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                results = soup.find_all('div', class_=['result', 'drive-result', 'item'])
                
                for result in results[:5]:
                    try:
                        title_elem = result.find(['h3', 'h4', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        
                        link_elem = result.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = PlacementDriveScraper.BASE_URL + link
                        
                        if title and link:
                            jobs.append({
                                'title': title,
                                'company': company,
                                'link': link,
                                'source': 'PlacementDrive',
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing search result: {e}")
                
                time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            logger.debug(f"PlacementDrive company search error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping PlacementDrive.in drives...")
        
        all_jobs = []
        
        # Get active drives
        all_jobs.extend(cls.scrape_drives())
        
        # Try searching for specific companies
        companies = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'Amazon']
        for company in companies:
            if len(all_jobs) < 20:
                all_jobs.extend(cls.scrape_by_company(company))
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            link = job.get('link', '')
            if link and link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 PlacementDrive: {len(unique_jobs)} drives")
        return unique_jobs


def scrape_placementdrive_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return PlacementDriveScraper.scrape(profile)
