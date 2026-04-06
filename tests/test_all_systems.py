#!/usr/bin/env python3
"""Quick system test - check all entry points"""

import subprocess
import sys

scripts = [
    ('job_scraper_3hr.py --once', 'Continuous Scraper (Single Cycle)'),
    ('telegram_bot.py --test', 'Telegram Bot'),
    ('cloud_run.py', 'Cloud Run Mode'),
]

for script, name in scripts:
    print(f"\n{'='*70}")
    print(f"TESTING: {name}")
    print(f"Command: python3 {script}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable] + script.split(), 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        # Show last 20 lines of output
        output = (result.stdout + result.stderr).strip()
        lines = output.split('\n')
        last_lines = lines[-20:] if lines else []
        print('\n'.join(last_lines) if last_lines else "(No output)")
        print(f"\n✅ Return Code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT (expected for long-running processes)")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print(f"\n{'='*70}")
print("TEST COMPLETE")
print(f"{'='*70}")
