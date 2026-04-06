#!/usr/bin/env python3
"""
AI Job Hunter - Telegram Bot Launcher
=====================================
Standalone script to start the Telegram bot.
Usage: python3 run_bot.py
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env-analyst
env_file = Path(__file__).parent / ".env-analyst"
if env_file.exists():
    # Manual sourcing since dotenv can't handle 'export' syntax
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line or '=' not in line:
                continue
            # Strip 'export ' prefix
            if line.startswith('export '):
                line = line[7:]
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            os.environ[key] = value

# Initialize database tables before bot starts
from database.engine import init_db
init_db()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if not bot_token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not set. Check .env-analyst")
        sys.exit(1)
    
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    if not gemini_key:
        logger.warning("⚠️ GEMINI_API_KEY not set — smart chat will be limited. Get one free at https://aistudio.google.com/apikey")
    
    logger.info("🤖 Starting AI Job Hunter Telegram Bot...")
    logger.info(f"   Gemini AI: {'✅ Active' if gemini_key else '⚠️ Inactive (no key)'}")
    
    from integration.telegram_bot import run_telegram_bot
    asyncio.run(run_telegram_bot(bot_token))

if __name__ == '__main__':
    main()
