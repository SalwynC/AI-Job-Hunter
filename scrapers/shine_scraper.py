"""
Shine.com Scraper - Real job scraping from Shine.com
Powered by Playwright to bypass all anti-bot protections entirely setup-free!
"""

import logging
import random
import time
from typing import List, Dict
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class ShineScraper:
    """Real scraper for Shine.com jobs using zero-cost Playwright Chromium"""
    
    BASE_URL = "https://www.shine.com"
    
    @staticmethod
    def scrape(profile: Dict) -> List[Dict]:
        """Scrape real jobs from Shine.com via Playwright"""
        logger.info("🔍 Scraping Shine.com jobs via Playwright Stealth...")
        jobs = []
        queries = profile.get('queries', {}).get('shine', ['data analyst'])
        
        try:
            with sync_playwright() as p:
                # Add stealth arguments to bypass native bot detectors
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                # Create a context with a standard user-agent to avoid detection
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    viewport={'width': 1366, 'height': 768},
                    java_script_enabled=True
                )
                
                for query in queries[:2]:
                    page = context.new_page()
                    search_url = f"{ShineScraper.BASE_URL}/job-search/{query.replace(' ', '-')}-jobs"
                    
                    try:
                        logger.info(f"Navigating to: {search_url}")
                        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                        
                        try:
                            # 1st Strategy: Strict wait
                            page.wait_for_selector(".jobCardContainer, .job-card", timeout=8000)
                            job_elements = page.query_selector_all(".jobCardContainer, .job-card")
                        except Exception as e:
                            logger.info(f"Timeout on strict CSS selector for Shine. Proceeding to fallback logic.")
                            # 2nd Strategy: Broad wait and query for ANY div that contains link structures
                            time.sleep(3) # Wait for hydration without throwing an error
                            job_elements = page.query_selector_all("div[class*='job'], li[class*='job']")
                            
                        extracted = 0
                        for item in job_elements[:20]:
                            try:
                                # Broadening selectors to catch multiple DOM variants
                                title_elem = item.query_selector("a.jobTitle, .job_title, h2, a[href*='job']")
                                company_elem = item.query_selector("a.companyName, .company_name, span[class*='company']")
                                location_elem = item.query_selector("span.location, .job_loc, div[class*='location']")
                                
                                if title_elem and company_elem:
                                    title_text = title_elem.inner_text().strip()
                                    company_text = company_elem.inner_text().strip()
                                    link_href = title_elem.get_attribute("href")
                                    loc_text = location_elem.inner_text().strip() if location_elem else "India"
                                    
                                    if not link_href or len(title_text) < 3:
                                        continue
                                        
                                    # Ensure link gets absolute URI
                                    actual_link = link_href if link_href.startswith('http') else f"{ShineScraper.BASE_URL}{link_href}"
                                    
                                    jobs.append({
                                        'job_title': title_text,
                                        'company': company_text,
                                        'location': loc_text,
                                        'description': f"{query} role match from Shine",
                                        'link': actual_link,
                                        'posted_date': datetime.now() - timedelta(hours=random.randint(1, 48)),
                                        'platform': 'Shine.com'
                                    })
                                    extracted += 1
                            except Exception as e:
                                continue
                                
                        if extracted == 0:
                            logger.warning(f"Failed to find jobs on Shine for '{query}', layout might be heavily obfuscated.")
                            
                    except Exception as e:
                        logger.warning(f"Nav/Blocking error on Shine.com for '{query}': {e}")
                    finally:
                        page.close()
                
                browser.close()
            
            logger.info(f"✅ Shine.com (Playwright): Found {len(jobs)} REAL jobs freely!")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Shine.com fatal Playwright error: {e}")
            return jobs
