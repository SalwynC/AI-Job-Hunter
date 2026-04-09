#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    🚀 AI JOB HUNTER DEPLOYMENT STARTING"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Load configuration
echo "📋 Loading configuration..."
if [ -f .env-analyst ]; then
    source .env-analyst
    echo "✅ Configuration loaded"
else
    echo "⚠️  .env-analyst not found; proceeding with environment variables"
fi
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
import os
sys.path.insert(0, os.getcwd())
try:
    from automation.hourly_scraper import JobPipeline
    from config.role_loader import load_role_profiles
    from database.engine import init_db
    print("✅ All core modules verified")
except Exception as e:
    print(f"❌ Error during module verification: {e}")
    sys.exit(1)
PYEOF

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                    ✅ DEPLOYMENT CONFIGURATION COMPLETE"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 System Configuration:"
echo "  • Status: Production Ready"
echo "  • Pipeline: Autonomous Multi-Role Scraper"
echo "  • Database: NeonDB / Local PostgreSQL"
echo "  • Features: Auto-Init DB + Env Pre-flight Check"
echo ""
echo "🚀 Starting one-time run..."
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Start one production-safe autonomous cycle
python3 main.py --once
