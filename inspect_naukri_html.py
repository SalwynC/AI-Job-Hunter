#!/usr/bin/env python3
"""
🔧 Naukri HTML Inspector
Finds the correct CSS selectors for job cards
"""

import requests
from bs4 import BeautifulSoup
import random
import json

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.naukri.com/',
    }

def inspect_naukri():
    """Fetch Naukri page and print HTML structure."""
    url = "https://www.naukri.com/search?keyword=data%20analyst&location=Bangalore&pageNo=1"
    
    print(f"Fetching: {url}")
    response = requests.get(url, headers=get_headers(), timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all possible job card containers
        print("\n" + "="*60)
        print("🔍 Searching for job card containers...")
        print("="*60)
        
        # Try common patterns
        patterns = [
            ('article.jobTuple', soup.find_all('article', class_='jobTuple')),
            ('article[data-jobcard]', soup.find_all('article', attrs={'data-jobcard': True})),
            ('div.jobTuple', soup.find_all('div', class_='jobTuple')),
            ('div[class*="jobCard"]', soup.find_all('div', class_=lambda x: x and 'job' in x.lower() and 'card' in x.lower())),
            ('div[class*="job"][class*="result"]', soup.find_all('div', class_=lambda x: x and 'job' in x.lower() and ('result' in x.lower() or 'item' in x.lower()))),
        ]
        
        for pattern_name, elements in patterns:
            if elements:
                print(f"\n✅ Found {len(elements)} elements with: {pattern_name}")
                if elements:
                    print(f"\nFirst element HTML:")
                    print(elements[0].prettify()[:500])
                    
                    # Inspect first job
                    first = elements[0]
                    print(f"\n📋 Element attributes:")
                    print(f"  - Tag: {first.name}")
                    print(f"  - Class: {first.get('class')}")
                    print(f"  - ID: {first.get('id')}")
                    
                    # Look for job title
                    title = first.find('a', class_='jobTitle') or first.find('a', class_=lambda x: x and 'title' in x.lower())
                    print(f"  - Title found: {bool(title)}")
                    
                    # Look for company
                    company = first.find('a', class_='companyName') or first.find('span', class_=lambda x: x and 'company' in x.lower())
                    print(f"  - Company found: {bool(company)}")
                    
                    # Look for location
                    location = first.find('span', class_='jobLocWdth') or first.find('span', class_=lambda x: x and 'location' in x.lower())
                    print(f"  - Location found: {bool(location)}")
        
        # Print all div classes for analysis
        print("\n" + "="*60)
        print("🏷️  All unique div classes (first 20):")
        print("="*60)
        
        divs = soup.find_all('div')
        classes = set()
        for div in divs[:100]:
            if div.get('class'):
                class_str = ' '.join(div.get('class'))
                if len(class_str) < 80:
                    classes.add(class_str)
        
        for i, cls in enumerate(sorted(classes)[:20]):
            print(f"  {i+1}. {cls}")
            
    else:
        print(f"❌ Failed to fetch page: {response.status_code}")

if __name__ == '__main__':
    inspect_naukri()
