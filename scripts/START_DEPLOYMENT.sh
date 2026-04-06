#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    🚀 AI JOB HUNTER DEPLOYMENT STARTING"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Load configuration
echo "📋 Loading configuration..."
source .env-analyst
echo "✅ Configuration loaded"
echo ""

# Check Python
echo "🔍 Checking Python..."
python3 --version
echo ""

# Check dependencies
echo "📦 Checking dependencies..."
pip3 list | grep -E "telegram|pandas|requests|beautifulsoup|schedule" || echo "⚠️  Some packages may be missing"
echo ""

# Verify modules
echo "✅ Verifying modules..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from automation.hourly_scraper import JobPipeline
    from config.role_loader import load_role_profile
    from scrapers.job_processor import process_jobs
    print("✅ All core modules verified")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYEOF

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    ✅ DEPLOYMENT CONFIGURATION COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 System Configuration:"
echo "  • Telegram Bot Token: [CONFIGURED]"
echo "  • Telegram Chat ID: [CONFIGURED]"
echo "  • Schedule: Every 30 minutes"
echo "  • Jobs per delivery: 25+"
echo "  • Platforms: Naukri + Internshala + Unstop"
echo "  • Features: ATS Scoring + Keywords + Buttons"
echo ""
echo "🚀 Starting scheduler..."
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Start one production-safe scheduler cycle
python3 job_scraper_3hr.py --once
