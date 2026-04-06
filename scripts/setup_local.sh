#!/bin/bash
# Quick setup for local development and testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🎯 AI Job Hunter - Local Setup"
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p logs data_storage data/runtime

# Check .env-analyst
if [ ! -f ".env-analyst" ]; then
    echo "⚠️  .env-analyst not found!"
    echo "Create one with your Telegram bot token:"
    echo ""
    echo "TELEGRAM_BOT_TOKEN=your_token"
    echo "TELEGRAM_CHAT_ID=your_chat_id"
    echo "TELEGRAM_API_ID=31092925"
    echo "TELEGRAM_API_HASH=eaa313a7296497a11c0f496fb6583f0e"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Load env (for sanity check)
echo ""
echo "🔍 Checking configuration..."
source <(grep -v '^#' .env-analyst | head -6 | grep -v '^$' | xargs)

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_token" ]; then
    echo "❌ Please set real TELEGRAM_BOT_TOKEN in .env-analyst"
    exit 1
fi

echo "✅ Configuration looks good!"

# Test imports
echo ""
echo "🧪 Running import tests..."
python3 -c "
import sys
sys.path.insert(0, '.')
from config.role_loader import load_role_profile
from scrapers.naukri_scraper import NaukriScraper
from telegram_bot import AIJobHunterBot
p = load_role_profile('cse_final_year_2026')
print(f'✅ Loaded role: {p[\"display_name\"]}')
print(f'✅ All imports successful')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  • Run continuous scraper: python3 job_scraper_3hr.py"
echo "  • Run once (for GH Actions): python3 job_scraper_3hr.py --once"
echo "  • Start supervisor: python3 scripts/supervisor.py"
echo "  • Run Telegram bot: python3 telegram_bot.py"
echo ""
