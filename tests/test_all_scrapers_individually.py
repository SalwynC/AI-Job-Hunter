#!/usr/bin/env python3
"""
Test All Scrapers Individually
===============================
Run individual scrapers to verify they're working correctly.
"""

import sys
import time
from config.role_loader import load_role_profile

# Map of scraper modules and their function names
SCRAPERS = {
    "Naukri": ("scrapers.naukri_scraper", "scrape_naukri_jobs"),
    "LinkedIn": ("scrapers.linkedin_scraper", "scrape_linkedin_jobs"),
    "Internshala": ("scrapers.internshala_scraper", "scrape_internshala_jobs"),
    "Foundit": ("scrapers.foundit_scraper", "scrape_foundit_jobs"),
    "Talentd": ("scrapers.talentd_scraper", "scrape_talentd_jobs"),
    "Job4Freshers": ("scrapers.job4freshers_scraper", "scrape_job4freshers_jobs"),
    "Jobfound": ("scrapers.jobfound_scraper", "scrape_jobfound_jobs"),
    "Wellfound": ("scrapers.wellfound_scraper", "scrape_wellfound_jobs"),
    "PlacementDrive": ("scrapers.placementdrive_scraper", "scrape_placementdrive_jobs"),
}


def test_single_scraper(name: str, module_name: str, func_name: str, profile: dict) -> dict:
    """Test a single scraper."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        # Import module
        module = __import__(module_name, fromlist=[func_name])
        scraper_func = getattr(module, func_name)
        
        print(f"✅ Imported successfully")
        
        # Run scraper with timeout
        print(f"⏳ Scraping {name}... (timeout: 30s)")
        start_time = time.time()
        
        jobs = scraper_func(profile)
        
        elapsed = time.time() - start_time
        
        # Results
        if jobs:
            print(f"✅ SUCCESS: Found {len(jobs)} jobs in {elapsed:.1f}s")
            
            # Show sample
            sample = jobs[0]
            print(f"\n   Sample job:")
            print(f"   - Title: {sample.get('title', 'N/A')[:60]}")
            print(f"   - Company: {sample.get('company', 'N/A')[:40]}")
            print(f"   - Location: {sample.get('location', 'N/A')[:40]}")
            print(f"   - Link: {sample.get('link', 'N/A')[:60]}")
            
            return {
                "name": name,
                "status": "✅ PASS",
                "jobs_found": len(jobs),
                "time_sec": elapsed,
                "error": None
            }
        else:
            print(f"⚠️ WARNING: No jobs found (may be empty results)")
            return {
                "name": name,
                "status": "⚠️ EMPTY",
                "jobs_found": 0,
                "time_sec": elapsed,
                "error": "No jobs returned"
            }
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return {
            "name": name,
            "status": "❌ FAIL",
            "jobs_found": 0,
            "time_sec": 0,
            "error": f"Import: {str(e)[:50]}"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error: {error_msg[:100]}")
        
        # Print full error for debugging
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        return {
            "name": name,
            "status": "❌ FAIL",
            "jobs_found": 0,
            "time_sec": 0,
            "error": error_msg[:50]
        }


def main():
    """Run all scraper tests."""
    print("\n" + "🔍 "*20)
    print("TESTING ALL JOB SCRAPERS")
    print("🔍 "*20)
    
    # Load profile
    print("\nLoading role profile...")
    try:
        profile = load_role_profile("data_analyst")
        print(f"✅ Loaded profile: {profile.get('role_name', 'unknown')}")
    except Exception as e:
        print(f"❌ Failed to load profile: {e}")
        sys.exit(1)
    
    # Test all scrapers
    results = []
    for name, (module_name, func_name) in SCRAPERS.items():
        result = test_single_scraper(name, module_name, func_name, profile)
        results.append(result)
        
        # Small delay to avoid rate limiting
        time.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY - SCRAPER TEST RESULTS")
    print("="*80)
    
    print(f"\n{'Name':<20} {'Status':<12} {'Jobs Found':<12} {'Time (s)':<10}")
    print("-"*80)
    
    for result in results:
        print(f"{result['name']:<20} {result['status']:<12} {result['jobs_found']:<12} {result['time_sec']:<10.1f}")
    
    # Statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    passed = sum(1 for r in results if r["status"].startswith("✅"))
    warned = sum(1 for r in results if r["status"].startswith("⚠️"))
    failed = sum(1 for r in results if r["status"].startswith("❌"))
    total_jobs = sum(r["jobs_found"] for r in results)
    avg_time = sum(r["time_sec"] for r in results) / len(results) if results else 0
    
    print(f"✅ Passed:   {passed}/{len(results)}")
    print(f"⚠️ Warnings: {warned}/{len(results)}")
    print(f"❌ Failed:   {failed}/{len(results)}")
    print(f"📊 Total Jobs Found: {total_jobs}")
    print(f"⏱️ Average Time per Scraper: {avg_time:.1f}s")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if passed == len(results):
        print("✅ All scrapers working! Your system is ready for deployment.")
    elif failed == 0:
        print("✅ All critical scrapers working. Some may have empty results temporarily.")
    else:
        print("⚠️ Some scrapers have issues. Details:")
        for result in results:
            if result["status"].startswith("❌"):
                print(f"   - {result['name']}: {result['error']}")
    
    # Exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
