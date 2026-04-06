"""
Updated Naukri scraper using API endpoint (more reliable than HTML scraping).
Works as of Jan 2025.
"""

import requests
import json
import logging
from typing import Dict, List, Any
import time
import random
from urllib.parse import quote

logger = logging.getLogger(__name__)


class NaukriAPIScraperV2:
    """Naukri.com scraper using undocumented API endpoint."""
    
    # API endpoint (reverse-engineered from browser requests)
    API_URL = "https://www.naukri.com/api/search/JobSearch"
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Return headers that look like a browser."""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.naukri.com/jobs',
            'X-Requested-With': 'XMLHttpRequest',
        }
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape jobs from Naukri using API endpoint."""
        jobs = []
        
        try:
            # Get job queries from profile
            queries = profile.get('queries', {}).get('naukri', ['data analyst'])
            experience_levels = profile.get('experience_level', [1, 2, 3])
            
            for keyword in queries[:2]:  # Limit to 2 keywords to avoid rate limiting
                logger.info(f"🔍 Scraping Naukri for: {keyword}")
                
                params = {
                    'keyword': keyword,
                    'pageNo': 1,
                    'noOfResults': 50,  # Max per page
                    'seniority': ','.join(map(str, experience_levels)),
                    'sort': 'recency',
                    'filters': 'location%7CIndia'  # India only
                }
                
                try:
                    response = requests.get(
                        NaukriAPIScraperV2.API_URL,
                        params=params,
                        headers=NaukriAPIScraperV2.get_headers(),
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        job_list = data.get('jobDetails', [])
                        
                        for job in job_list:
                            parsed_job = NaukriAPIScraperV2._parse_job(job)
                            if parsed_job:
                                jobs.append(parsed_job)
                        
                        logger.info(f"✅ Found {len(job_list)} jobs for '{keyword}'")
                    else:
                        logger.warning(f"⚠️ API returned status {response.status_code}")
                    
                except Exception as e:
                    logger.error(f"❌ Error scraping API: {e}")
                
                # Random delay to avoid rate limiting
                time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            logger.error(f"❌ Fatal error in Naukri scraper: {e}")
        
        return jobs[:100]  # Return max 100 jobs
    
    @staticmethod
    def _parse_job(job: Dict[str, Any]) -> Dict[str, Any]:
        """Parse job object from API response."""
        try:
            salary_text = job.get('salaryText', 'Not disclosed')
            salary_min, salary_max = NaukriAPIScraperV2._parse_salary(salary_text)
            
            return {
                'title': job.get('jobDescription', 'Unknown').strip(),
                'company': job.get('companyName', 'Unknown').strip(),
                'location': job.get('jobLocation', 'India'),
                'description': job.get('jobDescription', ''),
                'requirements': job.get('reqDetails', ''),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'salary_text': salary_text,
                'job_type': job.get('jobType', 'Job'),
                'link': f"https://www.naukri.com/job-listings-{job.get('jobId', '')}",
                'platform': 'Naukri',
                'posted_date': job.get('createdDate', ''),
                'experience_years': job.get('expMonthsRequired', 0) // 12,
            }
        except Exception as e:
            logger.debug(f"Error parsing job: {e}")
            return None
    
    @staticmethod
    def _parse_salary(salary_text: str) -> tuple:
        """Parse salary like '5-7 LPA' to (5, 7)."""
        import re
        try:
            match = re.search(r'(\d+)\s*[-–]\s*(\d+)', salary_text)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            
            match = re.search(r'(\d+)', salary_text)
            if match:
                val = int(match.group(1))
                return (val, val)
        except:
            pass
        return (0, 0)


def scrape_naukri_jobs(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Public interface."""
    return NaukriAPIScraperV2.scrape(profile)


if __name__ == '__main__':
    # Test
    test_profile = {
        'queries': {'naukri': ['python developer', 'data analyst']},
        'experience_level': [1, 2, 3]
    }
    
    jobs = scrape_naukri_jobs(test_profile)
    print(f"\n✅ Found {len(jobs)} jobs")
    if jobs:
        print(f"\nSample job: {json.dumps(jobs[0], indent=2)}")
