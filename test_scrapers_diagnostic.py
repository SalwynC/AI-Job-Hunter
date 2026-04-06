#!/usr/bin/env python3
"""
🔍 Diagnostic Script for Job Scrapers
Tests each scraper individually to identify root causes
Date: April 5, 2026
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import scrapers
from scrapers.naukri_scraper import NaukriScraper
from scrapers.internshala_scraper import InternshalaScaper
from scrapers.unstop_scraper import UnstopScraper
from scrapers.shine_scraper import ShineScraper
from scrapers.timesjobs_scraper import TimesJobsScraper

# Sample profile for testing
TEST_PROFILE = {
    'role_key': 'data_analyst',
    'preferred_locations': ['Bangalore', 'Delhi', 'Hyderabad'],
    'queries': {
        'naukri': ['data analyst', 'business analyst'],
        'internshala': ['internship'],
        'unstop': ['internship', 'job'],
        'shine': ['data analyst'],
        'timesjobs': ['data analyst']
    }
}

def test_scraper(name, scraper_class, profile, method='scrape'):
    """Test a single scraper and log results."""
    print(f"\n{'='*60}")
    print(f"🧪 Testing {name}")
    print(f"{'='*60}")
    print(f"Start Time: {datetime.now()}")
    
    try:
        if hasattr(scraper_class, method):
            scraper_func = getattr(scraper_class, method)
            start = time.time()
            
            if method == 'scrape':
                result = scraper_func(profile)
            else:
                result = scraper_func()
                
            elapsed = time.time() - start
            
            print(f"✅ Execution Time: {elapsed:.2f}s")
            print(f"📊 Jobs Returned: {len(result) if result else 0}")
            
            if result:
                print(f"\n📋 Sample Job:")
                print(json.dumps(result[0], indent=2, default=str))
            else:
                print(f"⚠️ No jobs returned!")
                print(f"Return Type: {type(result)}")
                print(f"Return Value: {result}")
            
            return {
                'name': name,
                'status': '✅ SUCCESS' if result else '❌ EMPTY',
                'count': len(result) if result else 0,
                'time': elapsed,
                'error': None
            }
        else:
            return {
                'name': name,
                'status': '❌ NO METHOD',
                'count': 0,
                'time': 0,
                'error': f'Method {method} not found'
            }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Exception Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        return {
            'name': name,
            'status': '❌ FAILED',
            'count': 0,
            'time': 0,
            'error': str(e)[:100]
        }

def main():
    """Run all scraper diagnostics."""
    print("\n" + "="*60)
    print("🔧 JOB SCRAPER DIAGNOSTIC TEST")
    print(f"Date: {datetime.now()}")
    print("="*60)
    
    results = []
    
    # Test each scraper
    scrapers = [
        ('Naukri', NaukriScraper),
        ('Internshala', InternshalaScaper),
        ('Unstop', UnstopScraper),
        ('Shine', ShineScraper),
        ('TimesJobs', TimesJobsScraper)
    ]
    
    for name, scraper_class in scrapers:
        result = test_scraper(name, scraper_class, TEST_PROFILE)
        results.append(result)
        time.sleep(2)  # Delay between requests
    
    # Summary Report
    print(f"\n\n{'='*60}")
    print("📈 DIAGNOSTIC SUMMARY")
    print(f"{'='*60}")
    print(f"{'Scraper':<15} {'Status':<12} {'Jobs':<8} {'Time':<8}")
    print("-" * 60)
    
    total_jobs = 0
    for r in results:
        status_icon = '✅' if r['count'] > 0 else '❌'
        print(f"{r['name']:<15} {r['status']:<12} {r['count']:<8} {r['time']:<8.2f}s")
        total_jobs += r['count']
        
        if r['error']:
            print(f"  └─ Error: {r['error']}")
    
    print("-" * 60)
    print(f"{'TOTAL':<15} {'':<12} {total_jobs:<8}")
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'total_jobs': total_jobs,
        'all_failed': all(r['count'] == 0 for r in results)
    }
    
    report_path = Path('data/diagnostic_report.json')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Report saved to: {report_path}")
    
    return 0 if total_jobs > 0 else 1

if __name__ == '__main__':
    sys.exit(main())
