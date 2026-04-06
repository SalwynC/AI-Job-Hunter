# 🤖 AI Job Hunter

Autonomous job scraper & Telegram bot for 2026 fresher and internship roles across India.  
Scrapes 13 portals every 2 hours via GitHub Actions — delivers Top Picks with package info directly to your Telegram.

## Features

- **13 Job Portals** — LinkedIn, Naukri, Internshala, Foundit, Wellfound, PlacementDrive, TalentD, JobFound, Shine, TimesJobs, Unstop, Job4Freshers, Free Portals
- **40 Role Profiles** — Data Analyst, Full Stack, MERN, Python Dev, ML Engineer, Business Analyst, and more
- **Playwright Stealth** — Bypasses Cloudflare & anti-bot protections on all JS-heavy sites
- **Gemini AI Scoring** — Each job auto-scored against your fresher profile
- **Cloud Native** — NeonDB (PostgreSQL) backend, GitHub Actions cron every 2 hours
- **Telegram Bot** — Chat to query jobs, get Top Picks with salary/package info, apply links

## Quick Start

### 1. Copy env template
```bash
cp .env-analyst.example .env-analyst
# Fill in your tokens (Telegram, Gemini, NeonDB)
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Run locally (single pass)
```bash
source .env-analyst
export PYTHONPATH=$(pwd)
python main.py --once
```

### 4. Start Telegram Bot
```bash
source .env-analyst
export PYTHONPATH=$(pwd)
python run_bot.py
```

## Cloud Deployment (GitHub Actions)

The workflow at `.github/workflows/scraper.yml` runs automatically every 2 hours.

**Set these GitHub Secrets** (`Settings → Secrets → Actions`):

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID |
| `TELEGRAM_API_ID` | From my.telegram.org |
| `TELEGRAM_API_HASH` | From my.telegram.org |
| `GEMINI_API_KEY` | From aistudio.google.com |
| `DATABASE_URL` | NeonDB PostgreSQL URL |

Then go to **Actions → Autonomous AI Job Hunter → Run workflow** to trigger manually.

## Project Structure

```
ai-job-automation/
├── main.py                    # Master orchestrator (run all 40 roles)
├── run_bot.py                 # Telegram bot entry point
├── requirements.txt
├── .github/workflows/
│   └── scraper.yml            # GitHub Actions cron automation
├── scrapers/                  # 13 individual job portal scrapers
├── automation/                # Pipeline, scheduling, daily storage
├── integration/telegram_bot.py # Bot command handlers + AI chat
├── database/                  # SQLAlchemy models + NeonDB engine
├── analysis/gemini_scoring.py # AI job scoring
├── filters/final_filter.py    # ATS filter
├── roles/role_profiles.yaml   # 40 role definitions
├── config/role_loader.py
└── scripts/
    ├── healthcheck.py
    ├── migrate_local_to_cloud.py  # SQLite → NeonDB migration
    └── job_digest_scheduler.py
```

## Stack

- **Python 3.11** · Playwright · BeautifulSoup4 · SQLAlchemy
- **Database**: NeonDB (PostgreSQL) — free tier, serverless
- **AI**: Google Gemini (`google-generativeai`)
- **Bot**: `python-telegram-bot` v20+
- **CI/CD**: GitHub Actions