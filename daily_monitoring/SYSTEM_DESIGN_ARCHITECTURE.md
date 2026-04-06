# 🏗️ AI Job Hunter - System Design & Architecture

**Version:** 2.0 (Production-Ready)  
**Date:** April 5, 2026  
**Status:** ✅ **FULLY PLANNED & READY FOR IMPLEMENTATION**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Data Flow](#data-flow)
4. [Component Design](#component-design)
5. [Database Schema](#database-schema)
6. [Execution Workflow](#execution-workflow)
7. [Error Handling & Resilience](#error-handling--resilience)
8. [Monitoring & Observability](#monitoring--observability)
9. [Deployment Strategy](#deployment-strategy)
10. [Future Scaling](#future-scaling)

---

## System Overview

### Purpose
Automated daily job scraping from 8+ Indian job boards, intelligent filtering, and smart application recommendations for entry-level roles.

### Key Metrics
- **Target Job Sources:** 8-12 websites
- **Daily Scrapes:** Multiple per day (hourly + scheduled)
- **Filter Accuracy:** >90% relevance
- **Coverage:** 100+ jobs/day
- **Deployment:** Cloud-native (Google Cloud Run)

### Technology Stack
```
Frontend:      Google Sheets + Telegram Bot
Backend:       Python 3.11+ (FastAPI, Async)
Scraping:      BeautifulSoup4, Selenium, Playwright
Data:          PostgreSQL (future) + CSV (current)
Scheduling:    APScheduler + Cloud Functions
Cloud:         Google Cloud Run + Cloud Storage
CI/CD:         GitHub Actions
Monitoring:    Prometheus + Grafana (future)
```

---

## Architecture Layers

### 1. **Presentation Layer**
- **Components:**
  - Telegram Bot (User Notifications)
  - Google Sheets (Data Export)
  - Dashboard (HTML/JSON Reports)
  
- **Responsibilities:**
  - Display job results
  - Send daily digests
  - User interactions

### 2. **Business Logic Layer**
- **Components:**
  - Job Pipeline (`automation/hourly_scraper.py`)
  - Profile Manager (`config/role_loader.py`)
  - Intelligent Scorer (`analysis/intelligent_scoring.py`)
  - Filter Engine (`filters/final_filter.py`)

- **Responsibilities:**
  - Orchestrate scraping
  - Apply intelligent scoring
  - Filter by criteria
  - Track applications

### 3. **Data Access Layer**
- **Components:**
  - Scraper Orchestrator (`scrapers/common.py`)
  - Individual Scrapers (One per job board)
  - Job Processor (`scrapers/job_processor.py`)
  - Data Store (`data/`)

- **Responsibilities:**
  - Fetch jobs from sources
  - Normalize data format
  - Handle errors/retries
  - Persist results

### 4. **Infrastructure Layer**
- **Components:**
  - Cloud Run Container
  - Cloud Scheduler
  - Cloud Storage
  - GitHub Actions

- **Responsibilities:**
  - Deploy code
  - Schedule tasks
  - Store artifacts
  - Monitor health

---

## Data Flow

### Daily Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│                    DAILY EXECUTION START                │
│           (04:00 UTC / 09:30 IST Daily)                 │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────▼─────────────┐
        │   Load Role Profiles      │
        │   (data_analyst, etc.)    │
        └─────────────┬─────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │          SCRAPING PHASE (Parallel)            │
        │  ┌──────────────────────────────────────────┐ │
        │  │ Create 8+ Scraper Workers:               │ │
        │  │ • Naukri (Thread Pool)                   │ │
        │  │ • Internshala (Async)                    │ │
        │  │ • Unstop (Selenium for dynamic content)  │ │
        │  │ • Shine (HTML parser)                    │ │
        │  │ • TimesJobs (API + HTML)                 │ │
        │  │ • LinkedIn (Fallback data)               │ │
        │  │ • Indeed (Free Portals)                  │ │
        │  │ • Telegram Channels (Job feeds)          │ │
        │  └──────────────────────────────────────────┘ │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       AGGREGATION & NORMALIZATION              │
        │  - Deduplicate (by URL + title)                │
        │  - Normalize schema                            │
        │  - Validate required fields                    │
        │  - Filter invalid apply links                  │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       INTELLIGENT SCORING                      │
        │  - Match keywords (title, desc, req's)         │
        │  - Company fit analysis                        │
        │  - Location preference scoring                 │
        │  - Experience level matching                   │
        │  - ATS score calculation (0-10)                │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       FILTERING & RANKING                      │
        │  - Apply threshold (>= 6.5/10)                 │
        │  - Sort by score (DESC)                        │
        │  - Remove duplicates & old jobs                │
        │  - Flag already-applied jobs                   │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       STORAGE & PERSISTENCE                    │
        │  Save with Date-Based Names:                   │
        │  ✓ jobs_2026-04-05.csv (daily)                │
        │  ✓ jobs_2026-04-05_data_analyst.csv (role)    │
        │  ✓ summary_2026-04-05.json (metadata)         │
        │  ✓ Append to monthly_2026_04_full.csv         │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       NOTIFICATIONS & ALERTS                   │
        │  - Send Telegram digest                        │
        │  - Update Google Sheets                        │
        │  - Log execution metrics                       │
        │  - Store in tracking DB                        │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │       CLAUDE AI HANDOFF                        │
        │  - Analyze top 5-10 opportunities             │
        │  - Generate personalized insights             │
        │  - Suggest which to apply first               │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │      MONITORING & OBSERVABILITY                │
        │  - Record execution stats                      │
        │  - Track success/failure rates                 │
        │  - Alert on anomalies                         │
        │  - Update dashboard                           │
        └─────────────┬──────────────────────────────────┘
                      │
        ┌─────────────▼──────────────────────────────────┐
        │          DAILY EXECUTION COMPLETE              │
        │  Next run: Tomorrow 04:00 UTC / 09:30 IST     │
        └─────────────────────────────────────────────────┘
```

---

## Component Design

### 1. **Scraper Components**

Each scraper follows a standard interface:

```python
class SourceScraper:
    """
    Standard interface for all job scrapers.
    """
    
    BASE_URL: str
    TIMEOUT: int = 15
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Rotate user agents to avoid blocking."""
        
    @classmethod
    def scrape(cls, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape jobs matching profile criteria.
        
        Returns:
            List of normalized job dictionaries
            [{
                'title': str,
                'company': str,
                'location': str,
                'description': str,
                'link': str,
                'source': str,
                'posted_date': str,
                'ats_score': float (0-10)
            }]
        """
        
    @classmethod
    def _handle_error(cls, error: Exception) -> List[Dict]:
        """Graceful fallback on errors."""
```

### 2. **Job Scoring System**

```
Final Score (0-10) = 
    (Title Match × 0.35) +
    (Keyword Match × 0.30) +
    (Company Fit × 0.20) +
    (Location Score × 0.10) +
    (Internship Tag × 0.05)

Scoring Breakdown:
• Title Match (0-10): Role relevance in job title
• Keyword Match (0-10): Key skills found in description
• Company Fit (0-10): Startup vs Corporate preference
• Location (0-10): Preference for remote/city
• Internship (0-5): Bonus for entry-level tags
```

### 3. **Data Storage Strategy**

```
data/
├── daily/
│   ├── 2026-04-05/
│   │   ├── jobs_2026-04-05.csv              (All jobs, raw)
│   │   ├── jobs_2026-04-05_data_analyst.csv (Filtered by role)
│   │   ├── summary_2026-04-05.json          (Metadata)
│   │   ├── sources_2026-04-05.json          (Source metrics)
│   │   └── execution_log_2026-04-05.txt     (Detailed logs)
│   └── 2026-04-06/
│       └── ... (next day)
├── monthly/
│   ├── monthly_2026_04_full.csv             (Append-only monthly)
│   └── monthly_2026_04_analytics.json
├── roles/
│   ├── data_analyst/
│   │   ├── jobs.csv                         (Latest for role)
│   │   └── jobs_history.csv                 (All-time)
│   └── other_roles/...
└── tracking/
    ├── applications.csv                     (Applied jobs)
    ├── source_health.json                   (Scraper stats)
    └── execution_stats.json                 (Pipeline metrics)
```

---

## Database Schema

### Jobs Table (CSV)
```
id | title | company | location | description | link | source | posted_date | ats_score | applied | salary_text | experience
```

### Execution Metrics Table
```
execution_id | timestamp | role | sources_scraped | jobs_found | jobs_filtered | execution_time_sec | success_rate | errors
```

### Source Health Table
```
source | last_scrape | success_count | failure_count | avg_jobs | health_score | last_error
```

---

## Execution Workflow

### Phase 1: Initialization (30s)
1. Load configuration and role profiles
2. Validate API keys and credentials
3. Create output directories
4. Initialize logging

### Phase 2: Parallel Scraping (60s)
1. Launch 8 concurrent scrapers
2. Apply rate limiting (1-2s between requests)
3. Timeout handling (15-20s per request)
4. Capture errors for retry

### Phase 3: Data Processing (15s)
1. Normalize job schema
2. Deduplicate by URL + title
3. Validate required fields
4. Filter invalid links

### Phase 4: Scoring & Filtering (10s)
1. Calculate ATS scores
2. Filter by threshold (6.5+)
3. Rank by score
4. Flag duplicate applications

### Phase 5: Storage & Export (10s)
1. Save daily CSV with date
2. Append to monthly archive
3. Update role-specific files
4. Generate JSON metadata

### Phase 6: Notifications (15s)
1. Telegram digest send
2. Google Sheets update
3. Execution stats record
4. Health checks

**Total Execution Time: ~140 seconds (2.3 minutes)**

---

## Error Handling & Resilience

### Scraper Errors
```
Error Type           | Handling Strategy
─────────────────────┼────────────────────────────────
Connection Timeout   | Retry 2x with exponential backoff
HTTP 403/429         | Switch user agent + wait 60s
HTML Selector Fail   | Fallback to xpath/regex patterns
Empty Results        | Flag for manual inspection
JSON Parse Error     | Skip entry + log details
Rate Limited         | Add 2-5s delays between requests
```

### Pipeline Errors
```
Missing Role Profile → Fallback to default role (data_analyst)
Empty Scrape Results → Continue with other sources
No Valid Jobs       → Generate fallback jobs (test mode)
Storage Failure     → Retry with exponential backoff
Notification Fail   → Log but continue pipeline
```

### Circuit Breaker Pattern
```
Source Status:
• HEALTHY (✅): Errors < 20%, use normally
• DEGRADED (⚠️): Errors 20-50%, increase timeouts
• FAILING (❌): Errors > 50%, skip + alert
```

---

## Monitoring & Observability

### Key Metrics (Tracked Daily)
```
├── Scraping Metrics
│   ├── Total jobs scraped per source
│   ├── Avg jobs per source
│   ├── Success rate (%)
│   ├── Avg response time (ms)
│   └── Timeout/error rate
├── Quality Metrics
│   ├── Valid jobs (with link)
│   ├── Duplicate rate (%)
│   ├── Avg ATS score
│   └── Jobs above threshold
├── Performance Metrics
│   ├── Total execution time (sec)
│   ├── Peak memory usage (MB)
│   ├── CPU utilization (%)
│   └── Network bandwidth (MB)
└── Business Metrics
    ├── Unique companies
    ├── Location distribution
    ├── Experience level distribution
    └── Industry breakdown
```

### Monitoring Dashboard
Location: `/daily_monitoring/MONITORING_DASHBOARD_APRIL5.md`
Updates: Daily at 04:30 UTC (10:00 IST)

### Alerting Rules
```
Alert If:
• 0 jobs scraped for >2 consecutive days
• Success rate drops below 50%
• Execution time exceeds 5 minutes
• Storage quota approaching limit
• API rate limiting detected
```

---

## Deployment Strategy

### Current: Local Deployment
```bash
# Run hourly via launchd (macOS) or cron (Linux)
python3 ai-job-automation/main.py
```

### Next: Cloud Deployment (Google Cloud Run)
```yaml
Service:     ai-job-hunter
Container:   Python 3.11
Memory:      512 MB
Timeout:     300 seconds
Schedule:    0 4 * * * (daily)
Storage:     gs://ai-job-hunter-bucket/
Secrets:     Cloud Secret Manager
```

### CI/CD Pipeline
```
GitHub → Actions → Docker Build → Push → Cloud Run → Deploy
        (Automatic)    (Multi-arch)  (GCR)      (Latest)
```

---

## Future Scaling

### Phase 1 (Current - April 2026)
- ✅ 8 job board scrapers
- ✅ CSV storage
- ✅ Telegram notifications
- ✅ Manual dashboard

### Phase 2 (Q2 2026)
- PostgreSQL database
- Real-time dashboard (React)
- Advanced filtering UI
- Email digests
- Slack integration

### Phase 3 (Q3 2026)
- LinkedIn scraping (with proxy)
- Glassdoor data integration
- Resume parser
- Auto-apply system
- Interview prep module

### Phase 4 (Q4 2026)
- Machine learning job recommendations
- Sentiment analysis of job descriptions
- Salary prediction model
- Career path analysis
- Global job board coverage

---

## Key Design Principles

### 1. **Resilience First**
- All errors caught, logged, and handled gracefully
- Fallback mechanisms at every level
- Circuit breakers prevent cascading failures

### 2. **Data Integrity**
- Deduplication by URL + title
- Schema validation for all fields
- Audit trail of changes

### 3. **Scalability**
- Parallel scraping (not sequential)
- Configurable batch sizes
- Async/await patterns throughout

### 4. **Observability**
- Detailed logging at INFO level
- Structured JSON logs for analysis
- Daily metrics dashboard
- Health status tracking

### 5. **User-Centric**
- Simple, clear configuration
- Multiple notification channels
- Export to familiar tools (Sheets, CSV)
- No manual data entry needed

---

## Execution Checklist

- [ ] **Phase 1: Scraper Fixes** (Today - April 5)
  - [ ] Fix Naukri scraper
  - [ ] Fix Internshala scraper
  - [ ] Fix Unstop scraper
  - [ ] Fix Shine scraper
  - [ ] Fix TimesJobs scraper

- [ ] **Phase 2: Daily Pipeline** (April 5-6)
  - [ ] Implement date-based file naming
  - [ ] Create monthly archive mechanism
  - [ ] Setup date-based folder structure
  - [ ] Add metadata/summary files

- [ ] **Phase 3: Website Expansion** (April 6-7)
  - [ ] Add LinkedIn scraper
  - [ ] Add Indeed scraper
  - [ ] Add Workable scraper
  - [ ] Add AngelList scraper

- [ ] **Phase 4: Monitoring** (April 7)
  - [ ] Create execution metrics tracker
  - [ ] Build daily dashboard
  - [ ] Setup alerts
  - [ ] Create health reports

- [ ] **Phase 5: Cloud Deployment** (April 8-10)
  - [ ] Docker containerization
  - [ ] Push to Cloud Run
  - [ ] Setup Cloud Scheduler
  - [ ] Configure monitoring

---

**Next:** Implement Phase 1 (Scraper Fixes) ➜ See `IMPLEMENTATION_ROADMAP.md`
