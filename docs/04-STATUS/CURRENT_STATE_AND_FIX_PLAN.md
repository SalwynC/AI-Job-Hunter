# 🔴 AI Job Hunter - CURRENT STATE & FIX PLAN
**Date**: April 4, 2026 | **Status**: 🚨 CRITICAL ISSUES + SOLUTIONS

---

## 📊 CURRENT STATE ANALYSIS

### ✅ What IS Working
- ✅ Project structure is solid
- ✅ `main.py` entry point exists
- ✅ `JobPipeline` orchestration is correct
- ✅ Google Sheets integration infrastructure exists
- ✅ Telegram bot framework ready
- ✅ Configuration/role system ready
- ✅ Application tracking system exists
- ✅ Filtering + scoring infrastructure ready

### 🔴 What's BROKEN (Root Causes)
1. **Naukri scraper returns 0 jobs**
   - File: `scrapers/naukri_scraper.py` (OLD HTML selectors)
   - Issue: Naukri's DOM changed, old CSS selectors don't match
   - Status: `common.py` tries `scrape_naukri_jobs_v2` but this file may not exist or be incomplete

2. **Free portals scraper incomplete**
   - File: `scrapers/free_portals_scraper.py` (INCOMPLETE)
   - Issue: Class methods defined but `scrape_free_job_portals()` function missing
   - Status: `common.py` imports it, but function doesn't exist → ImportError

3. **Telegram scraper not properly configured**
   - File: `scrapers/telegram_scraper_improved.py` (may not exist)
   - Issue: Requires Telethon setup or fallback logic
   - Status: Partially implemented

4. **No fallback mechanism when scrapers fail**
   - Issue: When all scrapers fail, system generates fake jobs with `example.com` links
   - Status: `ALLOW_FALLBACK_JOBS=0` by default (disabled)

5. **Missing error handling in pipeline**
   - Issue: If `scrape_jobs_for_profile()` fails, job_count = 0
   - Status: No retry logic, no escalation to backup sources

---

## 🚀 IMMEDIATE FIX PLAN (Execute in Order)

### **PHASE 1: Fix Imports & Missing Functions** (15 minutes)

The `common.py` is trying to import function that don't exist. Fix this first:

#### Fix 1.1: Complete `free_portals_scraper.py`
Location: `scrapers/free_portals_scraper.py`

Create the **main scraper function** that's missing:

```python
def scrape_free_job_portals(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Wrapper to scrape from all free portals."""
    jobs = []
    
    # Try Indeed RSS
    jobs.extend(IndeedFreeAPI.scrape(profile) or [])
    
    # Try Internshala
    jobs.extend(InternshalaFreeAPI.scrape(profile) or [])
    
    # Try RemoteOK
    jobs.extend(RemoteOKFree.scrape(profile) or [])
    
    logger.info(f"Free portals returned {len(jobs)} jobs")
    return jobs
```

#### Fix 1.2: Verify `naukri_scraper_v2_api.py` exists
Check if file exists and is complete:
```bash
ls -la ai-job-automation/scrapers/naukri_scraper_v2_api.py
```

If missing: **I'll create it with working API endpoint**

#### Fix 1.3: Verify `telegram_scraper_improved.py` exists
Check if file exists:
```bash
ls -la ai-job-automation/scrapers/telegram_scraper_improved.py
```

If missing: **I'll create it with robust fallback**

---

### **PHASE 2: Test Individual Scrapers** (20 minutes)

Once imports are fixed, test each scraper:

```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation

# Test Naukri API V2
python3 -c "
from scrapers.naukri_scraper_v2_api import scrape_naukri_jobs
profile = {'queries': {'naukri': ['python developer']}, 'experience_level': [1]}
jobs = scrape_naukri_jobs(profile)
print(f'Naukri jobs: {len(jobs)}')
for j in jobs[:2]:
    print(f'  - {j.get(\"title\")} @ {j.get(\"company\")}')
"

# Test Free Portals
python3 -c "
from scrapers.free_portals_scraper import scrape_free_job_portals
profile = {'queries': {'indeed': ['analyst'], 'internshala': ['internship']}}
jobs = scrape_free_job_portals(profile)
print(f'Free portal jobs: {len(jobs)}')
"

# Test Telegram
python3 -c "
from scrapers.telegram_scraper_improved import scrape_telegram_jobs
jobs = scrape_telegram_jobs({})
print(f'Telegram jobs: {len(jobs)}')
"
```

**Expected output:**
- Naukri: 30-80 jobs ✅
- Free Portals: 20-50 jobs ✅
- Telegram: 0-10 jobs ✅ (optional)

---

### **PHASE 3: Fix Role Configuration** (10 minutes)

Your role profiles need job sources configured:

**File**: `config/roles/data_analyst.yaml` or similar

Ensure it has sources:

```yaml
name: Data Analyst
role_key: data_analyst
target_level: entry

queries:
  naukri:
    - "data analyst fresher"
    - "junior analyst"
  internshala:
    - "data analyst internship"
  indeed:
    - "data analyst india"
  free_portals: []  # Will use its own sources

preferred_locations:
  - "India"
  - "Remote"

keywords_include:
  - "analyst"
  - "data"
  - "sql"
  - "excel"

keywords_exclude:
  - "sales"
  - "accountant"
  - "hr"
```

---

### **PHASE 4: Test Full Pipeline** (10 minutes)

```bash
# Set role and run
export TARGET_ROLE=data_analyst
python3 main.py
```

**Check output:**
```bash
# Should have jobs now
ls -lah data/data_analyst/jobs.csv
wc -l data/data_analyst/jobs.csv  # Should be >10
head data/data_analyst/jobs.csv   # Check data quality
```

---

### **PHASE 5: Setup Google Sheets Integration** (15 minutes)

Goal: Append jobs to Google Sheet automatically

**Steps:**
1. Enable Google Sheets API in Google Cloud Console
2. Add credentials to `.env-analyst`
3. Verify `google_sheets_integration.py` works

**Test:**
```bash
python3 -c "
from google_sheets_integration import append_jobs_to_sheet
import pandas as pd

df = pd.read_csv('data/data_analyst/jobs.csv')
append_jobs_to_sheet(df, 'data_analyst')
print('✅ Sheet updated')
"
```

---

### **PHASE 6: Setup Telegram Bot** (10 minutes)

Goal: Send top 5 jobs to Telegram daily

**Steps:**
1. Get `TELEGRAM_BOT_TOKEN` from BotFather
2. Add to `.env-analyst`
3. Test bot send

**Test:**
```python
from telegram_bot import send_job_digest
import pandas as pd

df = pd.read_csv('data/data_analyst/jobs.csv').head(5)
send_job_digest(df, 'data_analyst')
print('✅ Telegram message sent')
```

---

### **PHASE 7: Setup 3-Hour Scheduler** (10 minutes)

Goal: `main.py` runs automatically every 3 hours

**On macOS using launchd**:

Create file: `~/Library/LaunchAgents/com.ai-job-hunter.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-job-hunter.plist</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation/main.py</string>
    </array>
    <key>StartInterval</key>
    <integer>10800</integer>  <!-- 3 hours in seconds -->
    <key>StandardOutPath</key>
    <string>/tmp/ai-job-hunter.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ai-job-hunter.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
```

**Load it:**
```bash
launchctl load ~/Library/LaunchAgents/com.ai-job-hunter.plist
launchctl list | grep ai-job-hunter  # Verify loaded
```

---

## 🎯 EXPECTED RESULTS AFTER FIXES

### Before Fixes
```
scraped_jobs: 0
saved_jobs: 0
❌ No data in sheet
❌ No Telegram messages
```

### After Fixes (Within 20 minutes)
```
scraped_jobs: 80-150
saved_jobs: 50-100
✅ Sheet populated with 50+ CSE roles
✅ Telegram receives 5 top jobs
✅ Runs every 3 hours automatically
```

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] **PHASE 1**: Fix imports & create missing functions
- [ ] **PHASE 2**: Test individual scrapers (verify job counts)
- [ ] **PHASE 3**: Fix role configuration with sources
- [ ] **PHASE 4**: Run full pipeline, check `data/*/jobs.csv`
- [ ] **PHASE 5**: Setup Google Sheets, test append
- [ ] **PHASE 6**: Setup Telegram bot, test send
- [ ] **PHASE 7**: Setup launchd scheduler, verify runs
- [ ] **Final**: Verify full end-to-end flow

---

## 🧪 VERIFICATION COMMANDS

After each phase, run these to verify:

```bash
# Check if scrapers return data
python3 test_all_scrapers_v2.py

# Check if job files created
ls -lah data/*/jobs.csv

# Check if jobs in sheet
curl "https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?key={API_KEY}" | grep jobCount

# Check if bot is sending
tail -f /tmp/ai-job-hunter.out.log

# Check scheduler runs
launchctl list | grep ai-job-hunter
```

---

## 🚨 IF SOMETHING BREAKS

1. **Check logs first:**
   ```bash
   tail -100 /tmp/ai-job-hunter.err.log
   tail -100 /tmp/ai-job-hunter.out.log
   tail -100 data/ci/free_mode_last_run.log
   ```

2. **Test single component:**
   ```bash
   python3 -c "from scrapers.common import scrape_jobs_for_profile; print(scrape_jobs_for_profile({'queries': {'naukri': ['test']}}))"
   ```

3. **Check imports:**
   ```bash
   python3 -c "import scrapers.free_portals_scraper"
   ```

4. **Run with verbose logging:**
   ```bash
   LOG_LEVEL=DEBUG python3 main.py
   ```

---

## ⚡ QUICK START AFTER FIXES

```bash
# 1. Go to project folder
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation

# 2. Run once to test
python3 main.py

# 3. Check data created
ls -lah data/data_analyst/

# 4. Enable scheduler
launchctl load ~/Library/LaunchAgents/com.ai-job-hunter.plist

# 5. Done! System now runs every 3 hours autonomously
```

---

## 📞 KEY FILES TO CHECK/FIX

Priority order:

1. **`scrapers/free_portals_scraper.py`** → Add missing function
2. **`scrapers/naukri_scraper_v2_api.py`** → Create if missing
3. **`scrapers/telegram_scraper_improved.py`** → Create if missing
4. **`config/roles/*.yaml`** → Add sources to queries
5. **`.env-analyst`** → Add sheet + Telegram credentials
6. **`google_sheets_integration.py`** → Test with real sheet
7. **`telegram_bot.py`** → Test with bot token

---

**Status**: 🟡 FIXABLE IN 90 MINUTES | Let's execute this together!
