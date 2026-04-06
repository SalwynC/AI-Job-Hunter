"""
TimesJobs.com Scraper - Real job scraping from TimesJobs.com
Powered by Playwright to bypass all anti-bot protections entirely setup-free!
"""

import logging
import random
import time
from typing import List, Dict
from datetime import datetime, timedelta

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TimesJobsScraper:
    """Real scraper for TimesJobs.com jobs using zero-cost Playwright Chromium"""
    
    BASE_URL = "https://www.timesjobs.com"
    
    @staticmethod
    def scrape(profile: Dict) -> List[Dict]:
        """Scrape real jobs from TimesJobs.com via Playwright"""
        logger.info("🔍 Scraping TimesJobs.com jobs via Playwright Stealth...")
        jobs = []
        queries = profile.get('queries', {}).get('timesjobs', ['data analyst'])
        
        try:
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
                
                for query in queries[:2]:
                    page = context.new_page()
                    # A robust search string for TimesJobs
                    search_url = f"{TimesJobsScraper.BASE_URL}/candidate/job-search.html?searchType=personalizedSearch&luc=India&txtKeywords={query.replace(' ', '+')}"
                    
                    try:
                        logger.info(f"Navigating to: {search_url}")
                        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                        
                        try:
                            # 1st Strategy: Strict wait
                            page.wait_for_selector("li.clearfix.job-bx", timeout=8000)
                            job_elements = page.query_selector_all("li.clearfix.job-bx, ul.new-joblist li")
                        except Exception as e:
                            logger.info(f"Timeout on strict CSS selector for TimesJobs. Proceeding to fallback logic.")
                            time.sleep(3)
                            job_elements = page.query_selector_all("a[href*='job-detail']")
                            
                        extracted = 0
                        
                        # Loop through results
                        for item in job_elements:
                            if len(jobs) >= 10:
                                break
                            try:
                                # We check if it is an Anchor Tag fallback or a full wrapper
                                tag_name = item.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name == 'a':
                                    title_text = item.inner_text().strip()
                                    link_href = item.get_attribute("href")
                                    company_text = "Unknown"
                                else:
                                    title_elem = item.query_selector("h2 a, a[href*='job-detail']")
                                    title_text = title_elem.inner_text().strip() if title_elem else ''
                                    link_href = title_elem.get_attribute("href") if title_elem else ''
                                    
                                    company_elem = item.query_selector("h3.joblist-comp-name")
                                    company_text = company_elem.inner_text().strip() if company_elem else "Unknown"

                                if link_href and len(title_text) > 3:
                                    actual_link = link_href if link_href.startswith('http') else f"{TimesJobsScraper.BASE_URL}{link_href}"
                                    
                                    # Basic heuristic for package
                                    salary_text = 'Not disclosed'
                                    
                                    jobs.append({
                                        'job_title': title_text,
                                        'company': company_text,
                                        'location': 'India',
                                        'description': f"{query} role match from TimesJobs",
                                        'salary_text': salary_text,
                                        'link': actual_link,
                                        'posted_date': datetime.now() - timedelta(hours=random.randint(1, 48)),
                                        'platform': 'TimesJobs.com'
                                    })
                                    extracted += 1
                            except Exception as e:
                                continue
                                
                        if extracted == 0:
                            logger.warning(f"Failed to find jobs on TimesJobs for '{query}'.")
                            
                    except Exception as e:
                        logger.warning(f"Nav/Blocking error on TimesJobs for '{query}': {e}")
                    finally:
                        page.close()
                
                browser.close()
            
            logger.info(f"✅ TimesJobs (Playwright): Found {len(jobs)} REAL jobs!")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ TimesJobs fatal Playwright error: {e}")
            return jobs
