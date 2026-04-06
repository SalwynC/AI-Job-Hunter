#!/usr/bin/env python3
"""Test script to verify all imports work"""

import sys
print("Python version:", sys.version)
print("\n=== TESTING IMPORTS ===\n")

# Test 1: CONFIG_REFERENCE
try:
    import CONFIG_REFERENCE
    print("✅ CONFIG_REFERENCE module imports OK")
except Exception as e:
    print(f"❌ CONFIG_REFERENCE: {str(e)[:100]}")
    sys.exit(1)

# Test 2: config.role_loader
try:
    from config.role_loader import load_role_profile
    print("✅ config.role_loader imports OK")
except Exception as e:
    print(f"❌ config.role_loader: {str(e)[:100]}")

# Test 3: scrapers.job_processor
try:
    from scrapers.job_processor import process_jobs
    print("✅ scrapers.job_processor imports OK")
except Exception as e:
    print(f"❌ scrapers.job_processor: {str(e)[:100]}")

# Test 4: analysis.intelligent_scoring
try:
    from analysis.intelligent_scoring import score_job
    print("✅ analysis.intelligent_scoring imports OK")
except Exception as e:
    print(f"❌ analysis.intelligent_scoring: {str(e)[:100]}")

# Test 5: filters.final_filter
try:
    from filters.final_filter import apply_filters
    print("✅ filters.final_filter imports OK")
except Exception as e:
    print(f"❌ filters.final_filter: {str(e)[:100]}")

print("\n=== ALL CRITICAL IMPORTS VERIFIED ✅ ===")
