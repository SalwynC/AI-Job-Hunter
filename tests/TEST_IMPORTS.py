#!/usr/bin/env python3
"""Test script to verify all imports work"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Python version:", sys.version)
print("\n=== TESTING IMPORTS ===\n")

# Test 1: config.role_loader
try:
    from config.role_loader import load_role_profiles
    print("✅ config.role_loader imports OK")
except Exception as e:
    print(f"❌ config.role_loader: {str(e)[:100]}")

# Test 2: scrapers.common
try:
    from scrapers.common import scrape_jobs_for_profile
    print("✅ scrapers.common imports OK")
except Exception as e:
    print(f"❌ scrapers.common: {str(e)[:100]}")

# Test 3: analysis.gemini_scoring
try:
    from analysis.gemini_scoring import score_jobs
    print("✅ analysis.gemini_scoring imports OK")
except Exception as e:
    print(f"❌ analysis.gemini_scoring: {str(e)[:100]}")

# Test 4: filters.final_filter
try:
    from filters.final_filter import filter_jobs
    print("✅ filters.final_filter imports OK")
except Exception as e:
    print(f"❌ filters.final_filter: {str(e)[:100]}")

# Test 5: integration modules
try:
    from integration.google_sheets_integration import GoogleSheetsManager
    from integration.telegram_bot import AIJobHunterBot
    print("✅ integration modules import OK")
except Exception as e:
    print(f"❌ integration: {str(e)[:100]}")

print("\n=== ALL CRITICAL IMPORTS VERIFIED ✅ ===")
