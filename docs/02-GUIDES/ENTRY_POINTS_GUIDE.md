# Entry Points Guide - Which Script to Run?

**Date**: April 3, 2026  
**Status**: ✅ Clarified entry points after project cleanup

---

## 🎯 Quick Reference

| Script | Purpose | When to Use | Status |
|--------|---------|------------|--------|
| `job_scraper_3hr.py` | **Continuous 24/7 job scraper** | Local continuous background job | ✅ **ACTIVE** |
| `telegram_bot.py` | **Interactive Telegram bot** | User commands via Telegram chat | ✅ **ACTIVE** |
| `cloud_run.py` | **HTTP endpoint for cloud** | Cloud deployment (Render.com) | ✅ **ACTIVE** |
| `job_digest_scheduler.py` | **Scheduled digest sender** | Send daily job summaries | ✅ **ACTIVE** |
| `main.py` | **Single scraping cycle** | One-time manual job scraping | ⏳ Legacy |
| `google_sheets_integration.py` | **Google Sheets sync** | Sync jobs to Google Sheets | ⏳ Optional |

---

## 📍 Which Script for Your Use Case?

### Use Case 1: Local Development & Testing
```bash
# Run a single job scraping cycle
python main.py

# Monitor output, confirm jobs are found
```

### Use Case 2: Continuous Local Operation (Background Job)
```bash
# Run 24/7 scraper (runs in terminal, restart after interruption)
python job_scraper_3hr.py

# This will:
# - Scrape every 3 hours
# - Save jobs to CSV
# - Send to Telegram
# - Continue running until you Ctrl+C
```

### Use Case 3: Interactive Telegram Bot
```bash
# Start bot (responds to user commands)
python telegram_bot.py

# Users can type commands in Telegram:
# /start           - Show available commands
# /latest_jobs     - Get latest job listings
# /my_roles        - Show configured roles
# /status          - Check scraper status
```

### Use Case 4: Cloud Deployment (Render.com)
```bash
# This is what Render calls:
python cloud_run.py

# Listens on HTTP port 8000
# Responds to webhook triggers
# No terminal needed (runs as service)
```

### Use Case 5: Scheduled Digests Only
```bash
# Send daily summary emails/messages
python job_digest_scheduler.py

# Sends digest at configured time
# Requires scheduler to be running
```

---

## 🚀 Recommended Setup

### For Personal Use (Simplest)
```bash
# Terminal 1: Start the bot
python telegram_bot.py

# Terminal 2: Start continuous scraper
python job_scraper_3hr.py

# Now you have:
# ✓ Automatic jobs every 3 hours
# ✓ Interactive Telegram bot
# ✓ On-demand job requests via /latest_jobs
```

### For Production (Cloud)
```bash
# Deploy cloud_run.py to Render.com
# It handles everything automatically
# See PRODUCTION_CHECKLIST.md for details
```

### For Scheduled Digests Only
```bash
# Run one of these:
python job_digest_scheduler.py      # Daemon mode (recommended)
# OR
python main.py && python job_digest_scheduler.py  # One-time + digest
```

---

## 🔍 Script Details

### `job_scraper_3hr.py` (Main Scraper)

**What it does:**
- Scrapes 6 job platforms every 3 hours
- Deduplicates & filters jobs
- Scores with AI
- Saves to CSV
- Sends to Telegram

**When to use:**
- Want 24/7 automatic job scraping
- Running on your local machine
- Need continuous background operation

**How to run:**
```bash
python job_scraper_3hr.py
```

**How to stop:**
```
Press Ctrl+C in terminal
```

**Output:**
- CSV files in `data/jobs_csv/`
- Logs in `logs/`
- Telegram notifications sent

---

### `telegram_bot.py` (Interactive Bot)

**What it does:**
- Responds to Telegram commands
- Fetches latest jobs on demand
- Shows scraper status
- Configurable via chat

**When to use:**
- Want an interactive interface
- Need on-demand job requests
- Users sending commands via Telegram

**How to run:**
```bash
python telegram_bot.py
```

**Available commands:**
```
/start           - Show help
/latest_jobs     - Get recent jobs
/search <query>  - Search jobs
/status          - Scraper status
/config          - Show configuration
/stop            - Shutdown bot
```

**Output:**
- Direct Telegram messages
- Inline buttons for actions
- Formatted job listings

---

### `cloud_run.py` (Cloud Deployment)

**What it does:**
- Provides HTTP endpoint
- Handles webhook triggers
- Runs on cloud platform
- No terminal needed

**When to use:**
- Deploying to Render.com / Heroku / AWS
- Want serverless operation
- No local machine needed always on

**How to run:**
```bash
# Locally for testing:
python cloud_run.py

# On cloud platform (auto):
# Platform calls: python cloud_run.py
```

**Endpoints:**
```
POST /scrape           - Trigger immediate scrape
GET /status            - Check if running
GET /latest_jobs       - Get recent jobs
POST /send_telegram    - Send message to Telegram
```

**Output:**
- JSON responses
- Logs to cloud platform
- Telegram notifications

---

### `job_digest_scheduler.py` (Digest Sender)

**What it does:**
- Sends job summaries on schedule
- Combines jobs into digest
- Sends via Telegram/Email
- Configurable frequency

**When to use:**
- Want daily/weekly summaries
- Less frequent notifications
- Digest format preferred

**How to run:**
```bash
python job_digest_scheduler.py
```

**Output:**
- Scheduled messages sent
- Digest format (not individual jobs)
- Sends at configured time

---

### `main.py` (Legacy Single Cycle)

**What it does:**
- Runs one complete scraping cycle
- Exits after completion
- Good for testing/debugging

**When to use:**
- Quick manual scrape
- Testing configuration
- One-time job collection

**How to run:**
```bash
python main.py
```

**Output:**
- CSV file with jobs
- Console output
- Exits after finishing

---

### `google_sheets_integration.py` (Optional)

**What it does:**
- Syncs jobs to Google Sheets
- Creates/updates spreadsheet
- Maintains job history

**When to use:**
- Want spreadsheet view
- Team collaboration
- Historical tracking

**How to run:**
```bash
python google_sheets_integration.py
```

**Setup required:**
1. Create Google Sheet
2. Get Sheet ID from URL
3. Set `GOOGLE_SHEET_ID` in .env
4. Authenticate OAuth

**Output:**
- Updated Google Sheet
- Jobs formatted as rows

---

## 🎓 Common Scenarios

### Scenario 1: "I want jobs sent automatically every 3 hours"
```bash
python job_scraper_3hr.py
```
✅ This handles it automatically

---

### Scenario 2: "I want to check jobs manually from Telegram"
```bash
python telegram_bot.py
# Then in Telegram: /latest_jobs
```
✅ Bot runs, you request on-demand

---

### Scenario 3: "I want automatic scraping + manual checks"
```bash
# Terminal 1:
python job_scraper_3hr.py

# Terminal 2:
python telegram_bot.py

# Now bot serves requests while scraper runs
```
✅ Best of both

---

### Scenario 4: "I want cloud deployment with no local machine"
```
Deploy cloud_run.py to Render.com
(Configure webhook in Render dashboard)
```
✅ Cloud handles everything

---

### Scenario 5: "I want daily job digest emails"
```bash
python job_digest_scheduler.py
```
✅ Sends scheduled digests

---

## ⚡ Performance Notes

| Script | Memory | CPU | Network | Runs 24/7? | Cost |
|--------|--------|-----|---------|-----------|------|
| `main.py` | Low (50MB) | Medium | Medium | No | Free |
| `job_scraper_3hr.py` | Medium (150MB) | Medium | Continuous | Yes | Free (local) |
| `telegram_bot.py` | Low (100MB) | Low | Low | Yes | Free (local) |
| `cloud_run.py` | Low (100MB) | Low | On-demand | Yes | Free (Render tier) |
| `job_digest_scheduler.py` | Medium (150MB) | Low | Medium | Yes | Free (local) |

---

## 🔧 Troubleshooting Entry Points

**Issue**: "The script started but nothing is happening"
- Solution: Add `-v` or `--verbose` flag for debug output

**Issue**: "Script is using too much memory"
- Solution: Use `main.py` for one-time runs instead of continuous `job_scraper_3hr.py`

**Issue**: "Not sure which script is running"
- Solution: Check process list: `ps aux | grep python`

**Issue**: "All scripts are running and using resources"
- Solution: Kill unneeded ones: `pkill -f job_scraper_3hr.py`

See TROUBLESHOOTING.md for more help.

---

## 📋 Decision Tree

```
Do you want automatic job scraping?
├─ Yes, 24/7
│  └─→ Use: job_scraper_3hr.py
├─ Yes, on schedule (daily)
│  └─→ Use: job_digest_scheduler.py
└─ No, just on-demand
   └─→ Use: telegram_bot.py + /latest_jobs command

Also want interactive commands?
├─ Yes
│  └─→ Also run: telegram_bot.py
└─ No
   └─→ Use scraper only

Deploying to cloud?
├─ Yes
│  └─→ Use: cloud_run.py
└─ No (local machine)
   └─→ Use: job_scraper_3hr.py or telegram_bot.py
```

---

**Generated**: April 3, 2026  
**Status**: ✅ Entry points clarified after Phase A cleanup  
**Next**: See PRODUCTION_CHECKLIST.md for deployment
