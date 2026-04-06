#!/usr/bin/env python3
"""
Test Telegram Bot Integration
==============================
Verifies that Telegram bot can send and receive messages correctly.
Run this AFTER setting up your .env file with TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_connection():
    """Test if Telegram bot can connect."""
    print("\n" + "="*60)
    print("🤖 TESTING TELEGRAM BOT CONNECTION")
    print("="*60)
    
    try:
        from telegram import Bot
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("   Run: pip install python-telegram-bot")
        return False
    
    # Check credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not set in .env")
        return False
    
    print(f"✅ Bot token present: {bot_token[:15]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # Test connection
    try:
        bot = Bot(token=bot_token)
        me = bot.get_me()
        print(f"✅ Connected to bot: @{me.username}")
        print(f"   Name: {me.first_name}")
        print(f"   Bot ID: {me.id}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check your bot token is correct")
        print("   - Make sure bot was created via @BotFather")
        print("   - Check .env file has correct token")
        return False


def test_send_message():
    """Test sending a test message."""
    print("\n" + "="*60)
    print("📤 TESTING MESSAGE SENDING")
    print("="*60)
    
    try:
        from telegram import Bot
    except ImportError:
        print("❌ python-telegram-bot not installed")
        return False
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not (bot_token and chat_id):
        print("❌ Bot token or chat ID missing")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Send test message asynchronously
        async def send_test():
            message = await bot.send_message(
                chat_id=chat_id,
                text="✅ **AI Job Hunter Bot Test**\n\n"
                     "If you see this message, your Telegram integration is working!\n\n"
                     "🎯 Next steps:\n"
                     "1. Run your first job scrape\n"
                     "2. Check Google Sheets integration\n"
                     "3. Deploy to cloud\n"
                     "4. Enjoy automated job hunting! 🚀"
            )
            return message
        
        # Run async function synchronously
        loop = asyncio.get_event_loop()
        message = loop.run_until_complete(send_test())
        
        print(f"✅ Message sent successfully!")
        print(f"   Message ID: {message.message_id}")
        print(f"   Chat ID: {message.chat_id}")
        print(f"\n💬 Check your Telegram chat to verify message received")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Make sure chat ID is correct")
        print("   - Try sending /start to your bot first")
        print("   - Check Telegram privacy settings")
        return False


def test_job_scraping():
    """Test if job scraping works."""
    print("\n" + "="*60)
    print("🔍 TESTING JOB SCRAPING")
    print("="*60)
    
    try:
        from config.role_loader import load_role_profile
        from scrapers.common import scrape_jobs_for_profile
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        # Load role profile
        print("Loading role profile...")
        profile = load_role_profile("data_analyst")
        print(f"✅ Loaded profile: {profile.get('role_key', 'unknown')}")
        
        # Test a single scraper (use the fastest one)
        print("\nTesting Internshala scraper (should be fast)...")
        from scrapers.internshala_scraper import scrape_internshala_jobs
        
        jobs = scrape_internshala_jobs(profile)
        print(f"✅ Scraped {len(jobs)} jobs from Internshala")
        
        if jobs:
            # Show sample job structure
            sample_job = jobs[0]
            print("\n📋 Sample Job Structure:")
            for key in list(sample_job.keys())[:5]:
                value = str(sample_job[key])[:50]
                print(f"   {key}: {value}")
            return True
        else:
            print("⚠️ No jobs found (may be rate limited)")
            return True
            
    except Exception as e:
        print(f"⚠️ Scraping test failed: {e}")
        print("\n💡 This might be due to:")
        print("   - Website changes/updates")
        print("   - Rate limiting")
        print("   - Network issues")
        return False


def test_google_sheets_integration():
    """Test Google Sheets integration."""
    print("\n" + "="*60)
    print("📊 TESTING GOOGLE SHEETS INTEGRATION")
    print("="*60)
    
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
    except ImportError as e:
        print("❌ Required packages not installed")
        print("   Run: pip install gspread oauth2client")
        return False
    
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'credentials.json')
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    
    if not sheet_id:
        print("❌ GOOGLE_SHEETS_ID not set in .env")
        return False
    
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False
    
    try:
        print(f"Using credentials: {creds_path}")
        print(f"Sheet ID: {sheet_id}")
        
        # Authenticate
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        
        print("✅ Authenticated with Google Sheets")
        
        # Open sheet
        sheet = client.open_by_key(sheet_id)
        print(f"✅ Opened sheet: {sheet.title}")
        
        # Get first worksheet
        worksheet = sheet.get_worksheet(0)
        print(f"✅ Accessed worksheet: {worksheet.title}")
        print(f"   Rows: {worksheet.row_count}")
        print(f"   Columns: {worksheet.col_count}")
        
        # Try to append test row
        test_row = ["Test", "Company", "Location", "2026-04-04"]
        worksheet.append_row(test_row)
        print(f"✅ Test row appended successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets integration failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check credentials.json exists")
        print("   - Verify service account email has access to sheet")
        print("   - Check sheet ID is correct")
        return False


def main():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("AI JOB HUNTER - INTEGRATION TESTS")
    print("🚀 "*20)
    
    results = {
        "Telegram Connection": test_telegram_connection(),
        "Send Test Message": test_send_message(),
        "Job Scraping": test_job_scraping(),
        "Google Sheets": test_google_sheets_integration(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for deployment")
        return 0
    else:
        print("\n⚠️ Some tests failed. See troubleshooting above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
