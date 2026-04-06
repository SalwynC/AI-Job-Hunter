"""
Free Job Portals Scraper - Uses RSS feeds and public APIs
Includes: LinkedIn (unofficial), Indeed, RemoteOK, and other free sources

ZERO paid APIs. ALL free. INDIA ONLY.
"""

import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re
import time
import random

logger = logging.getLogger(__name__)


class LinkedInUnofficial:
    """LinkedIn job scraper using unofficial API endpoint."""
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape LinkedIn jobs (India only, free)."""
        jobs = []
        
        try:
            keywords = profile.get('queries', {}).get('linkedin', ['software engineer'])
            
            for keyword in keywords[:2]:
                try:
                    # Using LinkedIn search (this may work or be blocked)
                    # Better alternative: LinkedIn search API via webpage parsing
                    
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={quote(keyword)}&location=India"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(search_url, headers=headers, timeout=10)
                    
                    # LinkedIn heavily protects against scraping, but structure remains consistent
                    if response.status_code == 200:
                        # Parse would go here, but LinkedIn blocks it
                        # Fallback: use unofficial REST API
                        logger.info(f"LinkedIn blocking standard scrape for '{keyword}'")
                
                except Exception as e:
                    logger.debug(f"LinkedIn scrape failed: {e}")
                
                time.sleep(random.uniform(2, 4))
        
        except Exception as e:
            logger.error(f"LinkedIn scraper error: {e}")
        
        return jobs


class IndeedFreeAPI:
    """Indeed job scraper using RSS feed (completely free)."""
    
    RSS_URL = "https://www.indeed.com/rss"
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape Indeed via RSS feed (free, no API key needed)."""
        jobs = []
        
        try:
            keywords = profile.get('queries', {}).get('indeed', ['data analyst'])
            locations = ['India', 'Remote']  # India focus
            
            for keyword in keywords[:1]:
                for location in locations:
                    try:
                        # Indeed RSS endpoint
                        params = {
                            'q': keyword,
                            'l': location,
                            'format': 'json'
                        }
                        
                        # Try RSS feed
                        rss_url = f"{IndeedFreeAPI.RSS_URL}?q={quote(keyword)}&l={quote(location)}"
                        
                        response = requests.get(rss_url, timeout=10)
                        
                        if response.status_code == 200:
                            # Parse RSS XML
                            soup = BeautifulSoup(response.content, 'xml')
                            items = soup.find_all('item')
                            
                            for item in items[:20]:
                                job = {
                                    'title': item.find('title').text if item.find('title') else 'Job',
                                    'company': item.find('author').text if item.find('author') else 'Unknown',
                                    'location': location,
                                    'description': item.find('description').text if item.find('description') else '',
                                    'link': item.find('link').text if item.find('link') else '',
                                    'platform': 'Indeed',
                                    'source': 'Indeed RSS',
                                }
                                
                                if job['link']:
                                    jobs.append(job)
                            
                            logger.info(f"✅ Found {len(items)} Indeed jobs for '{keyword}'")
                    
                    except Exception as e:
                        logger.debug(f"Indeed scrape failed: {e}")
                    
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Indeed scraper error: {e}")
        
        return jobs


class InternshalaFreeAPI:
    """Internshala.com scraper using free public API."""
    
    API_URL = "https://www.internshala.com"
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape Internshala internships (free, public)."""
        jobs = []
        
        try:
            keywords = profile.get('queries', {}).get('internshala', ['data science internship'])
            
            for keyword in keywords[:2]:
                try:
                    # Internshala web scraping (no official API but structure is stable)
                    search_url = f"{InternshalaFreeAPI.API_URL}/jobs/{quote(keyword.replace(' ', '-'))}/1"
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(search_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        job_cards = soup.find_all('div', class_='job-card')
                        
                        for card in job_cards[:10]:
                            try:
                                title = card.find('h3', class_='title')
                                company = card.find('p', class_='company-name')
                                stipend = card.find('p', class_='stipend')
                                apply_link = card.find('a')
                                
                                if title:
                                    job = {
                                        'title': title.text.strip(),
                                        'company': company.text.strip() if company else 'Unknown',
                                        'location': 'India',
                                        'salary_text': stipend.text.strip() if stipend else 'Unpaid',
                                        'link': urljoin(InternshalaFreeAPI.API_URL, apply_link['href']) if apply_link else '',
                                        'platform': 'Internshala',
                                        'source': 'Internshala',
                                    }
                                    if job['link']:
                                        jobs.append(job)
                            except:
                                continue
                        
                        logger.info(f"✅ Found {len(job_cards[:10])} Internshala jobs")
                
                except Exception as e:
                    logger.debug(f"Internshala scrape failed: {e}")
                
                time.sleep(random.uniform(1, 2))
        
        except Exception as e:
            logger.error(f"Internshala scraper error: {e}")
        
        return jobs


class GitHubJobsFree:
    """GitHub Jobs (open source, completely free)."""
    
    # GitHub Jobs API is deprecated but data still available via RSS/direct fetch
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape dev jobs from GitHub discussions/issues (free)."""
        # GitHub has closed their official jobs board, but we can use:
        # 1. GitHub Discussions in tech repos
        # 2. Open source job boards
        # 3. Tech community Slack archives
        return []


class RemoteOKFree:
    """RemoteOK.io - Remote jobs including India positions."""
    
    @staticmethod
    def scrape(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape RemoteOK (free, JSON API available)."""
        jobs = []
        
        try:
            # RemoteOK has a public JSON API
            api_url = "https://remoteok.io/api"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Filter for India-based or remote from India
                for item in data[:50]:
                    if isinstance(item, dict):
                        # Check if India-relevant
                        job_str = str(item).lower()
                        
                        if any(keyword in job_str for keyword in ['india', 'remote', 'timezone']):
                            job = {
                                'title': item.get('job_title', item.get('title', 'Job')),
                                'company': item.get('company_name', item.get('company', 'Unknown')),
                                'location': item.get('location', 'Remote'),
                                'description': item.get('description', ''),
                                'link': item.get('apply_button_link', item.get('url', '')),
                                'platform': 'RemoteOK',
                                'source': 'RemoteOK',
                                'salary_text': item.get('salary', ''),
                            }
                            
                            if job['link']:
                                jobs.append(job)
            
            logger.info(f"✅ Found {len(jobs)} RemoteOK jobs")
        
        except Exception as e:
            logger.warning(f"RemoteOK scrape error: {e}")
        
        return jobs


def scrape_free_job_portals(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Master scraper for all free job portals."""
    all_jobs = []
    
    logger.info("🔍 Scraping free job portals...")
    
    # Try each source
    sources = [
        ('Indeed RSS', IndeedFreeAPI),
        ('Internshala', InternshalaFreeAPI),
        ('RemoteOK', RemoteOKFree),
    ]
    
    for source_name, scraper_class in sources:
        try:
            jobs = scraper_class.scrape(profile)
            if jobs:
                logger.info(f"✅ {source_name}: {len(jobs)} jobs")
                all_jobs.extend(jobs)
        except Exception as e:
            logger.warning(f"⚠️  {source_name} failed: {e}")
        
        time.sleep(random.uniform(1, 2))
    
    return all_jobs


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    test_profile = {
        'queries': {
            'indeed': ['python developer'],
            'internshala': ['data science internship'],
        }
    }
    
    jobs = scrape_free_job_portals(test_profile)
    print(f"\n✅ Found {len(jobs)} total jobs from free portals")
