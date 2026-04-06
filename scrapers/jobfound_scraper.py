"""
JobFound.org Scraper
Real scraping via Playwright to bypass protections.
"""

import logging
import time
from typing import Dict, List, Any
from urllib.parse import quote

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


class JobFoundScraper:
    """JobFound.org job scraper using Playwright."""
    
    BASE_URL = "https://www.jobfound.org"
    
    @staticmethod
    def scrape_listings(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape JobFound job listings."""
        jobs = []
        queries = profile.get('queries', {}).get('jobfound', ['software engineer'])
        
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
                
                for keyword in queries[:2]:
                    page = context.new_page()
                    search_url = f"{JobFoundScraper.BASE_URL}/?experience=0&jobType=internship%2Cfull+time&q={quote(keyword)}"
                    
                    try:
                        logger.info(f"Navigating to JobFound: {search_url}")
                        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
                        
                        try:
                            # Strict wait
                            page.wait_for_selector("a[href*='/job']", timeout=8000)
                        except Exception:
                            logger.info(f"Timeout on strict CSS selector for JobFound. Proceeding to fallback logic.")
                            time.sleep(3)
                            
                        job_elements = page.query_selector_all("a[href*='/job']")
                        
                        for item in job_elements:
                            if len(jobs) >= 10:
                                break
                            try:
                                link = item.get_attribute("href")
                                if not link:
                                    continue
                                if not link.startswith('http'):
                                    link = JobFoundScraper.BASE_URL + link

                                text = item.inner_text().strip()
                                # Basic heuristic: if the link text has multiple lines, it's a job card
                                parts = [p.strip() for p in text.split('\n') if p.strip()]
                                if len(parts) >= 2:
                                    title = parts[0]
                                    company = parts[1] if len(parts) > 1 else 'Company'
                                    location = parts[-1] if len(parts) > 2 else 'India'
                                else:
                                    # Fallback if it's a simple link
                                    title = text
                                    company = 'Company'
                                    location = 'India'
                                
                                if len(title) > 5 and 'job' not in title.lower() and title != 'Company':
                                    jobs.append({
                                        'title': title,
                                        'company': company,
                                        'location': location,
                                        'link': link,
                                        'source': 'JobFound',
                                    })
                            except Exception as e:
                                logger.debug(f"Error parsing JobFound job: {e}")
                                
                    except Exception as e:
                        logger.debug(f"JobFound search failed for '{keyword}': {e}")
                    finally:
                        page.close()
                browser.close()
        except Exception as e:
            logger.error(f"JobFound scraper error: {e}")
        
        return jobs
    
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scrape method."""
        logger.info("🔍 Scraping JobFound.org jobs...")
        jobs = cls.scrape_listings(profile)
        
        # Deduplicate
        seen = set()
        unique_jobs = []
        for job in jobs:
            link = job.get('link', '')
            if link and link not in seen:
                seen.add(link)
                unique_jobs.append(job)
        
        logger.info(f"📊 JobFound: {len(unique_jobs)} jobs")
        return unique_jobs

def scrape_jobfound_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Module interface function."""
    return JobFoundScraper.scrape(profile)
