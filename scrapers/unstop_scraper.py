"""
Unstop.com API/HTML Scraper - Real Implementation
Scrapes internship and job opportunities from Unstop
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import random
import urllib3
from typing import List, Dict, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class UnstopScraper:
    """Real Unstop.com scraper."""
    
    BASE_URL = "https://unstop.com"
    API_URL = "https://api.unstop.com/api/v1"
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    @staticmethod
    def get_headers():
        """Get random headers for requests."""
        return {
            'User-Agent': random.choice(UnstopScraper.USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://unstop.com/',
            'Connection': 'keep-alive'
        }
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape opportunities from Unstop."""
        logger.info("🔍 Scraping Unstop opportunities...")
        
        jobs = []
        
        try:
            # Try API endpoint first
            jobs_api = UnstopScraper.scrape_api(profile)
            jobs.extend(jobs_api)
            
            # Then try HTML scraping as fallback
            if len(jobs) < 10:
                jobs_html = UnstopScraper.scrape_html(profile)
                jobs.extend(jobs_html)
            
            if jobs:
                logger.info(f"📊 Total Unstop opportunities: {len(jobs)}")
            
        except Exception as e:
            logger.error(f"❌ Unstop scraper error: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_api(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Try to scrape via Unstop API."""
        logger.info("Attempting Unstop API...")
        
        jobs = []
        
        try:
            # Unstop API endpoint for internships/jobs
            categories = ['internships', 'entry-level-jobs']
            
            for category in categories:
                try:
                    url = f"{UnstopScraper.API_URL}/{category}?limit=20&offset=0"
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    response = requests.get(
                        url,
                        headers=UnstopScraper.get_headers(),
                        timeout=10,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        opportunities = data.get('data', [])
                        
                        for opp in opportunities[:10]:
                            job = {
                                'title': opp.get('title', 'Opportunity'),
                                'company': opp.get('organization', {}).get('name', 'Unknown'),
                                'location': opp.get('locations', [{}])[0].get('name', 'India') if opp.get('locations') else 'India',
                                'description': opp.get('description', ''),
                                'requirements': opp.get('eligibility', ''),
                                'salary_min': opp.get('stipend_from', 0) if 'internship' in category else opp.get('salary_from', 0),
                                'salary_max': opp.get('stipend_to', 0) if 'internship' in category else opp.get('salary_to', 0),
                                'job_type': 'Internship' if 'internship' in category else 'Job',
                                'link': opp.get('apply_link', f"https://unstop.com/o/{opp.get('id', '')}"),
                                'platform': 'Unstop',
                                'category': category,
                                'ats_score': 0,
                                'keywords_matched': []
                            }
                            jobs.append(job)
                        
                        logger.info(f"✅ Found {len(opportunities[:10])} {category} from Unstop API")
                    
                except Exception as e:
                    logger.debug(f"API error for {category}: {e}")
                    continue
        
        except Exception as e:
            logger.debug(f"Unstop API scraping failed: {e}")
        
        return jobs
    
    @staticmethod
    def scrape_html(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback HTML scraping for Unstop using stealth Playwright."""
        logger.info("Attempting Unstop HTML scraping via Playwright...")
        
        jobs = []
        queries = profile.get('queries', {}).get('unstop', ['data analyst'])
        
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    viewport={'width': 1366, 'height': 768},
                    java_script_enabled=True
                )
                
                for keyword in queries[:1]:
                    page = context.new_page()
                    # Example path for unstop, dynamic based on keyword
                    kw_fmt = keyword.replace(' ', '-')
                    url = f"{UnstopScraper.BASE_URL}/internships?searchTerm={keyword.replace(' ', '%20')}"
                    
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=20000)
                        
                        try:
                            # 1st Strategy: Strict wait
                            page.wait_for_selector(".opportunity-card", timeout=8000)
                            cards = page.query_selector_all(".opportunity-card, a[href*='/opportunity/']")
                        except Exception:
                            logger.info(f"Timeout on strict CSS selector for Unstop. Proceeding to fallback logic.")
                            time.sleep(3)
                            cards = page.query_selector_all("a")
                            
                        for card in cards:
                            if len(jobs) >= 10:
                                break
                            try:
                                link_href = card.get_attribute("href")
                                if not link_href or '/opportunity/' not in link_href and 'internships' not in link_href:
                                    continue
                                
                                title_text = card.inner_text().strip()
                                parts = [p.strip() for p in title_text.split('\n') if p.strip()]
                                
                                if len(parts) >= 2:
                                    title = parts[0]
                                    company = parts[1]
                                    location = parts[-1] if len(parts) > 2 else 'India'
                                else:
                                    title = title_text
                                    company = 'Unknown'
                                    location = 'India'
                                    
                                if 'job' in title.lower() or 'intern' in title.lower() or len(title) > 5:
                                    actual_link = link_href if link_href.startswith('http') else f"{UnstopScraper.BASE_URL}{link_href}"
                                    jobs.append({
                                        'title': title,
                                        'company': company,
                                        'location': location,
                                        'description': f"Match for {keyword}",
                                        'job_type': 'Internship',
                                        'salary_text': 'Not disclosed',
                                        'link': actual_link,
                                        'platform': 'Unstop',
                                        'source': 'Unstop'
                                    })
                            except Exception as e:
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Unstop Playwright scraping error: {e}")
                    finally:
                        page.close()
                browser.close()
        except Exception as e:
            logger.debug(f"Unstop HTML Playwright failed: {e}")
        
        return jobs


def scrape_unstop_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper function for compatibility."""
    return UnstopScraper.scrape(profile)
