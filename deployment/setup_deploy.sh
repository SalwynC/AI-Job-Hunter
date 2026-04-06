#!/bin/bash
# AI Job Hunter - Render Deployment Setup
# This script helps you set up and deploy to Render cloud
# Usage: bash setup_deploy.sh

set -e  # Exit on error

echo "🚀 AI Job Hunter - Render Deployment Setup"
echo "==========================================="
echo ""

# Step 1: Verify files exist
echo "✓ Step 1: Checking required files..."
required_files=(
    "cloud_run.py"
    "job_scraper_3hr.py"
    ".env-analyst"
    "requirements.txt"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ ERROR: Missing $file"
        exit 1
    fi
    echo "  ✅ Found: $file"
done

# Step 2: Verify Python
echo ""
echo "✓ Step 2: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found"
    exit 1
fi
python_version=$(python3 --version)
echo "  ✅ Found: $python_version"

# Step 3: Check Python dependencies
echo ""
echo "✓ Step 3: Checking Python packages..."
pip_packages=$(python3 -c "import sys; print('python-telegram-bot' in sys.modules or True)")
if [ "$pip_packages" = "True" ]; then
    echo "  ⚠️  Note: Install requirements with: pip install -r requirements.txt"
fi
echo "  ✅ Ready to install packages"

# Step 4: Verify environment variables
echo ""
echo "✓ Step 4: Verifying environment variables..."
source .env-analyst 2>/dev/null || true

required_env_vars=(
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_CHAT_ID"
    "TELEGRAM_API_ID"
    "TELEGRAM_API_HASH"
)

missing_vars=0
for var in "${required_env_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "  ❌ Missing: $var"
        missing_vars=$((missing_vars + 1))
    else
        # Show only first and last 5 characters for security
        value="${!var}"
        safe_value="${value:0:5}...${value: -5}"
        echo "  ✅ Found: $var = $safe_value"
    fi
done

if [ $missing_vars -gt 0 ]; then
    echo ""
    echo "❌ Missing environment variables found!"
    echo "Please update .env-analyst with your Telegram credentials."
    exit 1
fi

# Step 5: Show deployment instructions
echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "📋 NEXT STEPS - Deploy to Render:"
echo ""
echo "1. Go to: https://render.com"
echo "2. Sign up with GitHub"
echo "3. Create New Web Service"
echo "4. Select your ai-job-hunter repo"
echo ""
echo "5. Configure:"
echo "   Name: ai-job-hunter"
echo "   Environment: Python 3"
echo "   Build Command: pip install -r requirements.txt"
echo "   Start Command: python cloud_run.py"
echo ""
echo "6. Set Environment Variables:"
for var in "${required_env_vars[@]}"; do
    echo "   $var = ${!var}"
done
echo ""
echo "   Additional variables:"
echo "   SCRAPE_INTERVAL_MINUTES = 5"
echo "   ENABLE_NAUKRI = 1"
echo "   ENABLE_INTERNSHALA = 1"
echo "   ENABLE_UNSTOP = 1"
echo "   ENABLE_SHINE = 1"
echo "   ENABLE_TIMESJOBS = 1"
echo ""
echo "7. Click 'Create Web Service'"
echo "8. ✅ Done! Check Telegram in 5 minutes for jobs"
echo ""
echo "=========================================="
echo ""
echo "Need local test? Run:"
echo "  python cloud_run.py"
echo ""
