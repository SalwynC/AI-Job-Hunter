#!/usr/bin/env python3
"""
AI JOB HUNTER - STARTUP GUIDE & QUICK START
=============================================

This script provides a complete startup workflow.
Run this to get started with your AI Job Hunter system.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def print_header(text):
    """Print a nice header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(number, text):
    """Print a step indicator."""
    print(f"\n📍 STEP {number}: {text}")
    print("-" * 70)

def check_env_file():
    """Check if .env file exists."""
    print_step(1, "Checking Environment Configuration")
    
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file found")
        print("   Loading environment variables...")
        load_dotenv()
        
        # Check required variables
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "GOOGLE_SHEETS_ID"
        ]
        
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
                print(f"   ⚠️ {var}: NOT SET")
            else:
                masked = value[:10] + "..." if len(value) > 10 else value
                print(f"   ✅ {var}: {masked}")
        
        if missing:
            print(f"\n❌ Missing variables: {', '.join(missing)}")
            print("\n   To fix:")
            print("   1. Edit .env file")
            print("   2. Add missing values")
            print("   3. Save and run again")
            return False
        
        return True
    else:
        print("❌ .env file not found")
        print("\n   To create:")
        print("   1. Copy .env.template to .env")
        print("   2. Edit .env with your credentials")
        print("   3. Run again")
        
        if template_file.exists():
            print(f"\n   Command: cp {template_file} .env")
        
        return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print_step(2, "Checking Python Dependencies")
    
    required_packages = [
        ("telegram", "python-telegram-bot"),
        ("gspread", "gspread"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("beautifulsoup4", "beautifulsoup4"),
        ("selenium", "selenium"),
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\n   To install:")
        print("   pip install -r requirements.txt")
        print("\n   Or install individually:")
        for pkg in missing:
            print(f"   pip install {pkg}")
        return False
    
    return True


def check_credentials_file():
    """Check if Google Sheets credentials exist."""
    print_step(3, "Checking Google Sheets Credentials")
    
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
    
    if Path(creds_path).exists():
        print(f"✅ Credentials file found: {creds_path}")
        return True
    else:
        print(f"❌ Credentials file not found: {creds_path}")
        print("\n   To fix:")
        print("   1. Go to: https://console.cloud.google.com")
        print("   2. Create service account")
        print("   3. Download JSON key")
        print(f"   4. Save as {creds_path}")
        return False


def test_integrations():
    """Run integration tests."""
    print_step(4, "Testing Integrations")
    
    test_script = Path("test_integration.py")
    
    if not test_script.exists():
        print("❌ test_integration.py not found")
        return False
    
    print("Running integration tests...")
    print("(This may take a minute...)\n")
    
    result = subprocess.run(
        [sys.executable, str(test_script)],
        capture_output=False
    )
    
    return result.returncode == 0


def test_scrapers():
    """Run scraper tests."""
    print_step(5, "Testing Job Scrapers")
    
    script = Path("test_all_scrapers_individually.py")
    
    if not script.exists():
        print("❌ test_all_scrapers_individually.py not found")
        return False
    
    response = input("\nRun scraper tests now? (y/n): ").strip().lower()
    
    if response != "y":
        print("⏭️  Skipping scraper tests")
        return True
    
    print("\nRunning scraper tests...")
    print("(This may take 30-60 seconds...)\n")
    
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=False
    )
    
    return result.returncode == 0


def run_first_scrape():
    """Run the first job scrape."""
    print_step(6, "Running Your First Job Scrape")
    
    response = input("\nRun first job scrape now? (y/n): ").strip().lower()
    
    if response != "y":
        print("⏭️  Skipping first scrape")
        return True
    
    print("\nRunning job scrape...")
    print("(This may take 2-10 minutes depending on websites...)\n")
    
    try:
        from config.role_loader import load_role_profile
        from automation.hourly_scraper import JobPipeline
        
        # Load profile
        print("Loading role profile...")
        profile = load_role_profile("data_analyst")
        print(f"✅ Loaded: {profile.get('role_name', 'Unknown')}")
        
        # Run pipeline
        print("Starting job pipeline...")
        pipeline = JobPipeline(profile, run_profile="test", job_window="24h")
        result = pipeline.run()
        
        print("\n" + "="*60)
        print("📊 SCRAPE RESULTS")
        print("="*60)
        print(f"Role: {result['role']}")
        print(f"Jobs Scraped: {result['scraped_jobs']}")
        print(f"Jobs Saved: {result['saved_jobs']}")
        print(f"Output: {result['output_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_next_steps():
    """Show what to do next."""
    print_step(7, "Next Steps")
    
    print("""
✅ Your system is configured and tested!

Now you have 3 options:

1️⃣  **RUN MANUALLY (For Testing)**
   python3 main.py
   Scrapes jobs and sends to Telegram + Google Sheets
   Use this to test before deploying to cloud

2️⃣  **SCHEDULE LOCALLY (Development)**
   python3 job_digest_scheduler.py
   Runs job scraping every hour on your machine
   Use this while developing

3️⃣  **DEPLOY TO CLOUD (Production) ✨**
   Setup GitHub Actions for 24/7 free operation
   See: GITHUB_ACTIONS_SETUP.md
   Your jobs will run automatically every hour

📚 **DOCUMENTATION:**
   - Setup guide: SETUP_CHECKLIST.md
   - Project plan: PROJECT_ACTION_PLAN.md
   - Cloud deploy: GITHUB_ACTIONS_SETUP.md (see below for creation)
   - Troubleshooting: TROUBLESHOOTING.md

🎯 **RECOMMENDED PATH:**
   1. Run main.py manually a few times to test
   2. Verify jobs appear in Telegram
   3. Verify Google Sheets updates
   4. Deploy to GitHub Actions for 24/7 operation
   5. Monitor logs and make adjustments

📝 **QUICK COMMAND REFERENCE:**
   python3 main.py                      # Run once manually
   python3 job_digest_scheduler.py      # Schedule locally
   python3 test_integration.py          # Test all integrations
   python3 test_all_scrapers_individually.py  # Test each scraper

💡 **HOW IT WORKS:**
   1. System scrapes multiple job websites
   2. Filters and scores jobs by relevance
   3. Sends to your Telegram chat
   4. Updates your Google Sheets
   5. Repeats automatically

🚀 **READY TO GO LIVE?**
   See PROJECT_ACTION_PLAN.md Phase 4 for cloud deployment!

""")


def main():
    """Run complete startup."""
    print("🚀 "*20)
    print("AI JOB HUNTER - STARTUP WIZARD")
    print("🚀 "*20)
    
    print("\nThis wizard will help you get started with your AI Job Hunter system.")
    print("It checks your setup and runs initial tests.")
    
    checks = [
        ("Environment Configuration", check_env_file),
        ("Python Dependencies", check_dependencies),
        ("Google Sheets Credentials", check_credentials_file),
        ("Integration Tests", test_integrations),
        ("Scraper Tests", test_scrapers),
        ("First Job Scrape", run_first_scrape),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            results[check_name] = False
    
    # Summary
    print_header("STARTUP SUMMARY")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n{passed}/{total} checks passed\n")
    
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    if passed == total:
        print("\n🎉 All checks passed! Your system is ready!")
        show_next_steps()
        return 0
    else:
        print("\n⚠️ Some checks failed. See details above.")
        print("\nPlease fix the issues and run again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
