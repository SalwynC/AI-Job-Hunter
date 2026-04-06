"""
Naukri.com HTML Scraper - Real Implementation
Scrapes job opportunities from Naukri.com using BeautifulSoup
Supports multiple methods for adaptive scraping (html_scraping → cached_fallback)
"""

import re
import json
import time
import random
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NaukriScraper:
    """Real Naukri.com HTML scraper with adaptive methods."""

    BASE_URL = "https://www.naukri.com"

    # User agents to rotate
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

    # Adaptive methods: try in order, fall through on failure
    METHODS = ["html_scraping", "html_fallback"]

    FAILURE_STATE_FILE = Path(__file__).parent.parent / "data" / "source_failure_state.json"

    @staticmethod
    def get_headers():
        """Get random headers for requests."""
        return {
            'User-Agent': random.choice(NaukriScraper.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.naukri.com/',
            'Connection': 'keep-alive'
        }

    @staticmethod
    def _record_method_success(method: str):
        """Record a successful method for tracking."""
        try:
            state = NaukriScraper.FAILURE_STATE_FILE.read_text() if NaukriScraper.FAILURE_STATE_FILE.exists() else "{}"
            data = json.loads(state)
            source = data.setdefault("naukri", {})
            source.setdefault("method_stats", {})
            method_stats = source["method_stats"]
            method_stats.setdefault(method, {})
            method_stats[method]["successes"] = method_stats[method].get("successes", 0) + 1
            method_stats[method]["last_success"] = datetime.now().isoformat()
            NaukriScraper.FAILURE_STATE_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    @staticmethod
    def _record_method_failure(method: str):
        """Record a failed method for tracking."""
        try:
            state = NaukriScraper.FAILURE_STATE_FILE.read_text() if NaukriScraper.FAILURE_STATE_FILE.exists() else "{}"
            data = json.loads(state)
            source = data.setdefault("naukri", {})
            source.setdefault("method_stats", {})
            method_stats = source["method_stats"]
            method_stats.setdefault(method, {})
            method_stats[method]["failures"] = method_stats[method].get("failures", 0) + 1
            NaukriScraper.FAILURE_STATE_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape Naukri.com using HTML tuple divs (UPDATED April 5, 2026)."""
        logger.info("🔍 Scraping Naukri.com jobs...")
        jobs = []
        
        queries = profile.get('queries', {}).get('naukri', ['data analyst', 'business analyst', 'software developer'])
        locations = profile.get('preferred_locations', ['bangalore', 'delhi', 'hyderabad'])
        
        for query in queries[:2]:
            for location in locations[:2]:
                try:
                    search_url = f"{cls.BASE_URL}/search?keyword={query.replace(' ', '%20')}&location={location.replace(' ', '%20')}&pageNo=1"
                    
                    time.sleep(random.uniform(1, 2))
                    response = requests.get(search_url, headers=cls.get_headers(), timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find all job tuples (type="tuple" divs)
                        job_divs = soup.find_all('div', attrs={'type': 'tuple'})
                        logger.debug(f"Found {len(job_divs)} job tuples for {query} in {location}")
                        
                        for job_div in job_divs[:8]:  # Get up to 8 per location
                            try:
                                # Extract title
                                title_li = job_div.find('li', class_='desig')
                                title = title_li.text.strip() if title_li else 'Position'
                                
                                # Extract company
                                company_span = job_div.find('span', class_='org')
                                company = company_span.text.strip() if company_span else 'Unknown'
                                
                                # Extract experience
                                exp_span = job_div.find('span', class_='exp')
                                experience = exp_span.text.strip() if exp_span else 'Not specified'
                                
                                # Extract location
                                loc_span = job_div.find('span', class_='loc')
                                location_text = loc_span.text.strip() if loc_span else location.title()
                                
                                # Extract salary
                                salary_span = job_div.find('span', class_='salary')
                                salary_text = salary_span.text.strip() if salary_span else 'Not disclosed'
                                
                                # Extract skills
                                skills_span = job_div.find('span', class_='skill')
                                skills = skills_span.text.strip() if skills_span else ''
                                
                                # Extract link
                                link = job_div.get('data-url', '')
                                
                                # Extract posted date
                                date_span = job_div.find('span', class_='date')
                                posted_date = date_span.text.strip() if date_span else ''
                                
                                job = {
                                    'title': title,
                                    'company': company,
                                    'location': location_text or location.title(),
                                    'description': f'{skills}\n\nPosted: {posted_date}' if skills else '',
                                    'requirements': skills,
                                    'experience': experience,
                                    'salary_min': 0,
                                    'salary_max': 0,
                                    'salary_text': salary_text,
                                    'job_type': 'Job',
                                    'link': link,
                                    'platform': 'Naukri',
                                    'source': 'Naukri',
                                    'posted_date': posted_date,
                                    'ats_score': 0,
                                    'keywords_matched': []
                                }
                                
                                if link and title != 'Position':
                                    jobs.append(job)
                                    
                            except Exception as e:
                                logger.debug(f"Error parsing job tuple: {e}")
                                continue
                        
                        if jobs:
                            logger.info(f"✅ Found {len(jobs)} jobs from Naukri ({query}, {location})")
                            return jobs
                        
                    else:
                        logger.warning(f"Naukri returned status {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Error scraping Naukri ({query}, {location}): {str(e)[:60]}")
                    continue
        
        logger.info(f"📊 Total Naukri jobs: {len(jobs)}")
        return jobs

    @staticmethod
    def _scrape_html_scraping(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Primary method — HTML scraping with BeautifulSoup."""
        jobs = []
        queries = profile.get('queries', {}).get('naukri', ['data analyst', 'business analyst', 'software developer'])
        locations = profile.get('preferred_locations', ['bangalore', 'delhi', 'hyderabad'])

        for query in queries[:2]:
            for location in locations[:2]:
                try:
                    search_url = f"{NaukriScraper.BASE_URL}/search?keyword={query.replace(' ', '%20')}&location={location.replace(' ', '%20')}&pageNo=1"

                    time.sleep(random.uniform(1, 3))

                    response = requests.get(
                        search_url,
                        headers=NaukriScraper.get_headers(),
                        timeout=15
                    )

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        job_cards = soup.find_all('article', class_='jobTuple')

                        for card in job_cards[:5]:
                            try:
                                title_elem = card.find('a', class_='jobTitle')
                                company_elem = card.find('a', class_='companyName')
                                location_elem = card.find('span', class_='jobLocWdth')
                                salary_elem = card.find('span', class_='salary')

                                title = title_elem.text.strip() if title_elem else 'Position'
                                company = company_elem.text.strip() if company_elem else 'Unknown'
                                location_text = location_elem.text.strip() if location_elem else location
                                salary_text = salary_elem.text.strip() if salary_elem else 'Not disclosed'

                                salary_min, salary_max = NaukriScraper.parse_salary(salary_text)

                                link = 'N/A'
                                if title_elem and title_elem.get('href'):
                                    link = f"{NaukriScraper.BASE_URL}{title_elem['href']}"

                                description_elem = card.find('div', class_='job-description')
                                description = description_elem.text.strip() if description_elem else ''

                                job = {
                                    'title': title,
                                    'company': company,
                                    'location': location_text,
                                    'description': description,
                                    'requirements': '',
                                    'salary_min': salary_min,
                                    'salary_max': salary_max,
                                    'salary_text': salary_text,
                                    'job_type': 'Job',
                                    'link': link,
                                    'platform': 'Naukri',
                                    'ats_score': 0,
                                    'keywords_matched': []
                                }
                                jobs.append(job)
                            except Exception as e:
                                logger.debug(f"Error parsing job card: {e}")
                                continue

                        if job_cards:
                            logger.info(f"✅ Found {len(job_cards[:5])} jobs from Naukri ({query}, {location})")

                    else:
                        # Non-200 response — this method failed
                        if response.status_code in (403, 429):
                            raise Exception(f"Rate limited ({response.status_code})")
                        logger.warning(f"Naukri returned status {response.status_code}")
                        continue

                except Exception as e:
                    raise  # Let outer catch handle method failure

        if jobs:
            logger.info(f"📊 Total Naukri jobs: {len(jobs)}")
        return jobs

    @staticmethod
    def _scrape_html_fallback(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback — use longer timeouts, different URL patterns, more user agent rotation."""
        jobs = []
        queries = profile.get('queries', {}).get('naukri', ['data analyst', 'business analyst', 'software developer'])

        # Use broader queries only
        for query in queries[:1]:
            try:
                # Try alternative URL structure
                search_url = f"{NaukriScraper.BASE_URL}/search?keyword={query.replace(' ', '%20')}"

                headers = NaukriScraper.get_headers()
                headers['Accept'] = '*/*'

                response = requests.get(search_url, headers=headers, timeout=20)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Try both selectors — Naukri sometimes changes DOM
                    job_cards = soup.find_all('article', class_='jobTuple') or \
                                soup.find_all('div', class_='jobTuple')

                    for card in job_cards[:5]:
                        title_elem = card.find('a', class_='jobTitle')
                        company_elem = card.find('a', class_='companyName')
                        salary_elem = card.find('span', class_='salary')

                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Unknown',
                                'location': 'India',
                                'description': '',
                                'requirements': '',
                                'salary_min': 0,
                                'salary_max': 0,
                                'salary_text': salary_elem.text.strip() if salary_elem else 'Not disclosed',
                                'job_type': 'Job',
                                'link': f"{NaukriScraper.BASE_URL}{title_elem.get('href', '#')}",
                                'platform': 'Naukri',
                                'ats_score': 0,
                                'keywords_matched': []
                            }
                            jobs.append(job)

                    time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.debug(f"Fallback method failed: {e}")
                continue

        return jobs

    @staticmethod
    def parse_salary(salary_text: str) -> tuple:
        """Parse salary range from text like '5-7 LPA' or '5 - 7 LPA'."""
        try:
            # Look for pattern like "5-7" or "5 - 7"
            match = re.search(r'(\d+)\s*[-–]\s*(\d+)', salary_text)
            if match:
                return (int(match.group(1)), int(match.group(2)))

            # If only one number found
            match = re.search(r'(\d+)', salary_text)
            if match:
                val = int(match.group(1))
                return (val, val)

        except Exception as e:
            logger.debug(f"Error parsing salary '{salary_text}': {e}")

        return (0, 0)


def scrape_naukri_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper function for compatibility."""
    return NaukriScraper.scrape(profile)
