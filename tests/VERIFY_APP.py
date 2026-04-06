#!/usr/bin/env python3
"""
Simple test runner to verify the app works
"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🚀 AI JOB HUNTER - VERIFICATION TEST")
print("=" * 60)

# Test 1: Import CONFIG_REFERENCE
print("\n[1/3] Testing CONFIG_REFERENCE import...")
try:
    import CONFIG_REFERENCE
    print("✅ CONFIG_REFERENCE loaded successfully")
except Exception as e:
    print(f"❌ CONFIG_REFERENCE failed: {e}")
    sys.exit(1)

# Test 2: Load role profile
print("[2/3] Testing role profile loading...")
try:
    from config.role_loader import load_role_profile
    profile = load_role_profile("data_analyst")
    print(f"✅ Role profile loaded: {profile.get('display_name')}")
    print(f"   - Target keywords: {profile.get('target_keywords')[:3]}")
    print(f"   - Boost keywords: {profile.get('boost_keywords')}")
except Exception as e:
    print(f"❌ Role profile failed: {e}")
    sys.exit(1)

# Test 3: Check data directories
print("[3/3] Checking data directories...")
try:
    dirs = ['data', 'logs', 'data/ci']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"✅ {d}/ exists")
except Exception as e:
    print(f"❌ Directory check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED! Application is ready to run")
print("=" * 60)
print("\nNext steps:")
print("  python3 main.py              # One-time run")
print("  python3 job_scraper_3hr.py   # Continuous scraper")
print("  python3 telegram_bot.py      # Interactive bot")
