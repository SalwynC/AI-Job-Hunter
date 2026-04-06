# 🚀 AI Job Hunter - Implementation Roadmap

**Status:** Ready for Execution  
**Timeline:** April 5-12, 2026  
**Target:** **Complete + Production-Ready System**

---

## 🎯 Execution Plan (5 Phases)

### ⏱️ Phase Timeline
```
Phase 1 (SCRAPER FIXES)   Apr 5  | 2-3 hours  | Fix all 5 main scrapers
Phase 2 (DAILY PIPELINE)  Apr 5-6| 1-2 hours  | Date-based storage + archiving  
Phase 3 (EXPANSION)       Apr 6-7| 2-3 hours  | Add 4+ new job boards
Phase 4 (MONITORING)      Apr 7  | 1-2 hours  | Build tracking dashboard
Phase 5 (CLOUD DEPLOY)    Apr 8-10| 3-4 hours | Cloud Run + Scheduler setup
```

---

## Phase 1: Scraper Fixes (Apr 5) ⚡ START HERE!

### 1.1 Naukri.com Scraper Fix
**Problem:** CSS selectors changed, returning 0 jobs

**Solution:**
```python
# OLD (broken): article.jobTuple
# NEW (working): div[type="tuple"]    # New HTML structure

Changes needed:
• Update CSS selector: article.jobTuple → div[type="tuple"]
• Add retry logic with exponential backoff
• Better error messages
• Handle pagination properly
```

**File:** `/ai-job-automation/scrapers/naukri_scraper.py`
**Expected Result:** ✅ 10-20 jobs per search

---

### 1.2 Internshala.com Scraper Fix  
**Problem:** API endpoint returns 404 (deprecated)

**Solution:**
```python  
# OLD (broken): API endpoint https://api.internshala.com/...
# NEW (working): HTML scraping of /internships/ page

Changes needed:
• Switch from API to HTML scraping
• Find internship divs with correct selectors
• Extract company, title, location from HTML
• Build apply URLs correctly
```

**File:** `/ai-job-automation/scrapers/internshala_scraper.py`
**Expected Result:** ✅ 15-30 internships per fetch

---

### 1.3 Unstop.com Scraper Fix
**Problem:** API returns empty results, HTML structure unclear

**Solution:**
```python
# Use Selenium for JavaScript-rendered content
# Or find correct API endpoint with auth

Changes needed:
• Test with Selenium/Playwright for dynamic content
• Find correct API headers/auth
• Parse JSON responses correctly
• Handle pagination
```

**File:** `/ai-job-automation/scrapers/unstop_scraper.py`
**Expected Result:** ✅ 8-15 opportunities per search

---

### 1.4 Shine.com Scraper Fix
**Problem:** HTML selectors not matching current website

**Solution:**
```python
# Inspect HTML, find correct job container divs
# Update selectors and parsing logic

Changes needed:
• Use browser dev tools to find correct selectors
• Update CSS selectors
• Parse all job fields correctly
• Test with multiple pages
```

**File:** `/ai-job-automation/scrapers/shine_scraper.py`
**Expected Result:** ✅ 10-20 jobs per search

---

### 1.5 TimesJobs.com Scraper Fix
**Problem:** Missing or incorrect selectors

**Solution:**
```python
# Similar to Shine - inspect & update selectors
# Add proper error handling

Changes needed:
• Inspect current HTML structure
• Update all CSS selectors
• Add logging for debugging
• Make timeout configurable
```

**File:** `/ai-job-automation/scrapers/timesjobs_scraper.py`
**Expected Result:** ✅ 8-15 jobs per search

---

### Verification Commands (Phase 1)
```bash
# Test each scraper individually
cd ai-job-automation

# Naukri
python3 -c "
from scrapers.naukri_scraper import scrape_naukri_jobs
from config.role_loader import load_role_profile
profile = load_role_profile('data_analyst')
jobs = scrape_naukri_jobs(profile)
print(f'✅ Naukri: {len(jobs)} jobs'); print(jobs[:1] if jobs else 'NO JOBS')
"

# Internshala  
python3 -c "
from scrapers.internshala_scraper import scrape_internshala_jobs
from config.role_loader import load_role_profile
profile = load_role_profile('data_analyst')
jobs = scrape_internshala_jobs(profile)
print(f'✅ Internshala: {len(jobs)} jobs'); print(jobs[:1] if jobs else 'NO JOBS')
"

# Unstop
python3 -c "
from scrapers.unstop_scraper import scrape_unstop_jobs
from config.role_loader import load_role_profile
profile = load_role_profile('data_analyst')
jobs = scrape_unstop_jobs(profile)
print(f'✅ Unstop: {len(jobs)} jobs'); print(jobs[:1] if jobs else 'NO JOBS')
"

# And so on for each scraper...
```

---

## Phase 2: Daily Pipeline Enhancement (Apr 5-6)

### 2.1 Date-Based File Naming System

**Current:** `data/data_analyst/jobs.csv`  
**New:** `data/daily/2026-04-05/jobs_2026-04-05.csv`

**Implementation:**
```python
# File: automation/daily_storage.py (NEW)

from datetime import datetime
from pathlib import Path

class DailyStorage:
    """Handle daily, role-specific, and archival storage."""
    
    @staticmethod
    def get_daily_dir(date=None):
        """Get directory for date (default: today)."""
        date = date or datetime.utcnow().date()
        return Path("data/daily") / str(date)
    
    @staticmethod
    def save_daily_jobs(df, role, date=None):
        """Save jobs to: data/daily/2026-04-05/jobs_2026-04-05_data_analyst.csv"""
        date = date or datetime.utcnow().date()
        daily_dir = DailyStorage.get_daily_dir(date)
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"jobs_{date}_{role}.csv"
        filepath = daily_dir / filename
        df.to_csv(filepath, index=False)
        return filepath
    
    @staticmethod
    def save_monthly_archive(df, date=None):
        """Append to: data/monthly/monthly_2026_04_full.csv"""
        date = date or datetime.utcnow().date()
        month_str = date.strftime("%Y_%m")
        
        archive_dir = Path("data/monthly")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = archive_dir / f"monthly_{month_str}_full.csv"
        
        if filepath.exists():
            # Append (avoid duplicates by link)
            existing = pd.read_csv(filepath)
            combined = pd.concat([existing, df])
            combined = combined.drop_duplicates(subset=['link'], keep='first')
            combined.to_csv(filepath, index=False)
        else:
            # Create new
            df.to_csv(filepath, index=False)
        
        return filepath
    
    @staticmethod  
    def save_metadata(stats, date=None):
        """Save: data/daily/2026-04-05/summary_2026-04-05.json"""
        date = date or datetime.utcnow().date()
        daily_dir = DailyStorage.get_daily_dir(date)
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"summary_{date}.json"
        filepath = daily_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return filepath
```

**Integration Points:**
```python
# In automation/hourly_scraper.py (JobPipeline)

def save_outputs(self, df):
    """Save with new date-based system."""
    from automation.daily_storage import DailyStorage
    
    # Save daily file
    daily_path = DailyStorage.save_daily_jobs(df, self.profile['role_key'])
    logger.info(f"📅 Saved daily: {daily_path}")
    
    # Append to monthly archive
    archive_path = DailyStorage.save_monthly_archive(df)
    logger.info(f"📦 Appended to monthly: {archive_path}")
    
    # Save metadata
    stats = {
        "role": self.profile["role_key"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "jobs_count": len(df),
        "execution_time_sec": self.execution_time,
        "sources_used": df['source'].unique().tolist(),
    }
    summary_path = DailyStorage.save_metadata(stats)
    logger.info(f"📊 Saved summary: {summary_path}")
```

**Result:** Files organized by date:
```
data/
├── daily/
│   ├── 2026-04-05/
│   │   ├── jobs_2026-04-05.csv
│   │   ├── jobs_2026-04-05_data_analyst.csv
│   │   ├── summary_2026-04-05.json
│   │   └── sources_2026-04-05.json
│   ├── 2026-04-06/
│   │   └── ...
│   └── 2026-04-07/
│       └── ...
├── monthly/
│   ├── monthly_2026_04_full.csv (all April jobs)
│   └── monthly_2026_05_full.csv (will start May 1)
└── roles/
    └── data_analyst/
        └── jobs.csv (latest)
```

---

### 2.2 Execution Metrics Tracking

**File:** `/ai-job-automation/tracking/execution_tracker.py` (NEW)

```python
class ExecutionTracker:
    """Track daily execution metrics."""
    
    @staticmethod
    def log_execution(role, stats):
        """Log execution to: data/tracking/executions.csv"""
        tracking_dir = Path("data/tracking")
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        execution_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "date": datetime.utcnow().date(),
            "role": role,
            "jobs_scraped": stats.get("scraped_count", 0),
            "jobs_filtered": stats.get("filtered_count", 0),
            "execution_time_sec": stats.get("execution_time", 0),
            "success_rate": stats.get("success_rate", 0),
            "sources_used": stats.get("sources_used_count", 0),
        }
        
        filepath = tracking_dir / "executions.csv"
        
        if filepath.exists():
            existing = pd.read_csv(filepath)
            combined = pd.concat([existing, pd.DataFrame([execution_record])])
            combined.to_csv(filepath, index=False)
        else:
            pd.DataFrame([execution_record]).to_csv(filepath, index=False)
        
        return execution_record
```

---

## Phase 3: Website Expansion (Apr 6-7)

### 3.1 Add 4 New Job Boards

**New Scrapers to Create:**

#### A. LinkedIn Jobs (with proxy)
```python
# File: scrapers/linkedin_jobs_scraper.py
# Library: selenium + undetected_chromedriver (bypass detection)
# Strategy: Use proxies to avoid blocking
# Expected: 5-15 jobs per search
```

#### B. Indeed.com
```python
# File: scrapers/indeed_scraper.py
# Library: requests + BeautifulSoup
# URL: https://www.indeed.com/jobs?q={query}&l=India
# Expected: 10-20 jobs per page
```

#### C. Workable.com
```python
# File: scrapers/workable_scraper.py
# Strategy: Scrape company careers pages
# Expected: 8-12 jobs
```

#### D. AngelList (Wellfound) 
```python
# File: scrapers/wellfound_scraper.py
# Strategy: Startup job board (exists but improve)
# Expected: 5-10 startup jobs
```

**Total Coverage After Phase 3:**
- ✅ Naukri (Fixed)
- ✅ Internshala (Fixed)
- ✅ Unstop (Fixed)
- ✅ Shine (Fixed)
- ✅ TimesJobs (Fixed)
- ✅ LinkedIn (New)
- ✅ Indeed (New)
- ✅ Workable (New)
- ✅ AngelList/Wellfound (Enhanced)

**Expected daily yield:** 80-150+ jobs across 9 sources!

---

## Phase 4: Monitoring Dashboard (Apr 7)

### 4.1 Daily Metrics Dashboard

**File:** `/daily_monitoring/DAILY_EXECUTION_METRICS_APRIL.md`

Auto-updates daily with:
```
📊 DAILY EXECUTION SUMMARY
Date: 2026-04-05
═══════════════════════════════════════════

SCRAPING PHASE
┌──────────────────────────────────────────┐
│ Source          | Jobs | Success | Time  │
├──────────────────────────────────────────┤
│ Naukri          │ 12   │ ✅     │ 2.1s  │
│ Internshala     │ 14   │ ✅     │ 1.8s  │
│ Unstop          │ 8    │ ✅     │ 2.3s  │
│ Shine           │ 11   │ ✅     │ 1.9s  │
│ TimesJobs       │ 9    │ ✅     │ 1.7s  │
│ LinkedIn        │ 6    │ ⚠️     │ 4.2s  │
│ Indeed          │ 18   │ ✅     │ 2.5s  │
│ Workable        │ 4    │ ✅     │ 1.4s  │
└──────────────────────────────────────────┘
Total: 82 jobs scraped | Avg time: 2.2s
Success rate: 87.5% (7/8 sources)

FILTERING PHASE
├─ Started with: 82 jobs
├─ Duplicates removed: 5
├─ Invalid links: 2
├─ Below threshold: 18
└─ Final: 57 jobs (quality jobs)

TOP 5 JOBS TODAY
1. Data Analyst @ Tech Company (Bangalore) - Score: 9.2
2. Business Analyst Intern (Remote) - Score: 8.7
3. Data Engineer Entry (Hyderabad) - Score: 8.3
...

SYSTEM HEALTH
├─ Uptime: 99.8%
├─ Memory: 245 MB / 512 MB
├─ CPU: 12.3% avg
└─ Next run: 2026-04-06 04:00 UTC
```

---

## Phase 5: Cloud Deployment (Apr 8-10)

### 5.1 Docker Containerization
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python3", "cloud_run.py"]
```

### 5.2 Cloud Run Deployment
```bash
# Build and push
gcloud builds submit --tag gcr.io/{PROJECT}/ai-job-hunter

# Deploy
gcloud run deploy ai-job-hunter \
  --image gcr.io/{PROJECT}/ai-job-hunter \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx,ANTHROPIC_API=yyy
```

### 5.3 Cloud Scheduler Setup
```yaml
# Daily schedule  
Service: Cloud Scheduler
Frequency: 0 4 * * * (04:00 UTC)
Target: Cloud Run (ai-job-hunter)
Retry Policy: 2 retries with exponential backoff
```

---

## 📋 Complete Checklist

### Phase 1: Scraper Fixes
- [ ] **Naukri Scraper**
  - [ ] Update CSS selectors
  - [ ] Test with data_analyst query
  - [ ] Verify >10 jobs returned
  - [ ] Commit & document

- [ ] **Internshala Scraper**
  - [ ] Switch to HTML scraping
  - [ ] Update selectors
  - [ ] Test pagination
  - [ ] Verify >15 jobs returned

- [ ] **Unstop Scraper**
  - [ ] Test current implementation
  - [ ] Try Selenium if needed
  - [ ] Update selectors
  - [ ] Verify >8 jobs returned

- [ ] **Shine Scraper**
  - [ ] Inspect HTML structure
  - [ ] Update all selectors
  - [ ] Test with multiple queries
  - [ ] Verify >10 jobs returned

- [ ] **TimesJobs Scraper**
  - [ ] Update selectors
  - [ ] Add error handling
  - [ ] Test thoroughly
  - [ ] Verify >8 jobs returned

### Phase 2: Daily Pipeline
- [ ] Create `automation/daily_storage.py`
- [ ] Create `tracking/execution_tracker.py`
- [ ] Update `automation/hourly_scraper.py`
- [ ] Test date-based file creation
- [ ] Test monthly archive append
- [ ] Test metadata saving
- [ ] Verify directory structure

### Phase 3: Website Expansion
- [ ] Create LinkedIn scraper
- [ ] Create Indeed scraper
- [ ] Create Workable scraper
- [ ] Enhance Wellfound scraper
- [ ] Update `scrapers/common.py`
- [ ] Test all 9 sources in parallel
- [ ] Document new sources

### Phase 4: Monitoring
- [ ] Create execution metrics tracker
- [ ] Build daily dashboard file
- [ ] Setup auto-update script
- [ ] Create health status summary
- [ ] Setup alert rules

### Phase 5: Cloud Deployment
- [ ] Create Dockerfile
- [ ] Test local build
- [ ] Push to Google Container Registry
- [ ] Deploy to Cloud Run
- [ ] Configure Cloud Scheduler
- [ ] Setup monitoring & alerts
- [ ] Execute final test run

---

## 🎬 How to Use This Roadmap

1. **Read Phase 1 completely** - Understand the scraper fixes needed
2. **Implement Phase 1** - Fix all 5 scrapers
3. **Test Phase 1** - Run verification commands
4. **Move to Phase 2** - Implement date-based storage
5. **Complete all 5 phases** - Systematic completion

**Estimated Total Time:** 8-10 hours of focused work
**Expected Result:** **Complete, production-ready system**

---

**Next Steps:** 
1. Read SYSTEM_DESIGN_ARCHITECTURE.md (this document)
2. Start with Phase 1 implementation
3. Update this checklist as you progress
4. Create execution logs for each phase

**Let's Build This! 🚀**
