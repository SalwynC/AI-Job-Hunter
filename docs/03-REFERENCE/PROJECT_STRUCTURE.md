# AI Job Automation - Project Structure Map

**Last Updated:** 2024
**Status:** Reorganized & Documented

---

## 📊 Architecture Overview

```
ai-job-automation/
├── Core Entry Points
├── Configuration Management
├── Modular Subsystems
├── Data & Storage
├── Testing Framework
└── Documentation
```

---

## 🗂️ Directory Structure & Purpose

### **Root Level**
| File | Purpose |
|------|---------|
| `main.py` | Primary entry point for job hunting automation |
| `README.md` | Project overview and quick-start guide |
| `CONFIG_REFERENCE.py` | Configuration constants and references |

---

### **`ai/` - AI/LLM Integration**
Core AI capabilities for job applications and analysis.

```
ai/
├── resume_builder.py        # Generate/customize resumes
├── cover_letter_generator.py # Create cover letters  
├── job_matcher.py           # Match jobs to profile
├── interview_prep.py        # Interview preparation tools
└── application_writer.py    # Write application content
```

**Key Functions:**
- Resume generation and customization
- Cover letter creation (context-aware)
- Job matching algorithms
- Interview preparation assistance

---

### **`automation/` - Workflow Automation**
Orchestrates job hunting workflows and automation tasks.

```
automation/
├── job_hunter_workflow.py   # Main automation workflow
├── scheduler.py             # Task scheduling
├── parallel_processor.py     # Parallel job processing
├── batch_processor.py        # Batch application handling
└── workflow_state.py         # State management
```

**Key Functions:**
- Automated job applications
- Task scheduling and execution
- Parallel processing of jobs
- Batch operations handling

---

### **`scrapers/` - Web Scraping**
Extracts job data from various platforms.

```
scrapers/
├── linkedin_scraper.py      # LinkedIn job extraction
├── indeed_scraper.py        # Indeed job extraction
├── glassdoor_scraper.py     # Glassdoor job extraction
├── job_board_scraper.py     # Generic job board scraper
├── website_scraper.py       # General website scraping
└── api_client.py            # API interactions
```

**Supported Platforms:**
- LinkedIn
- Indeed
- Glassdoor
- Custom job boards

---

### **`filters/` - Job Filtering & Analysis**
Intelligent filtering and analysis of job postings.

```
filters/
├── salary_filter.py         # Salary range filtering
├── location_filter.py       # Geographic filtering
├── skills_matcher.py        # Skills matching
├── experience_filter.py     # Experience level filtering
├── company_filter.py        # Company filtering (size, industry)
├── red_flag_detector.py     # Detect problematic postings
└── advanced_analysis.py     # Complex filtering logic
```

**Filtering Dimensions:**
- Salary expectations
- Location preferences
- Required skills match
- Experience level
- Company characteristics
- Quality indicators

---

### **`roles/` - Job Role Classification**
Categorizes and standardizes job roles.

```
roles/
├── role_classifier.py       # Role categorization
├── role_definitions.py      # Role type definitions
├── seniority_mapper.py      # Seniority level mapping
└── specialization_mapper.py # Technical specialization mapping
```

**Features:**
- Standardized role classification
- Seniority level detection
- Specialization tracking

---

### **`integrations/` - External Integrations**
Connects with external tools and services.

```
integrations/
├── email_integration.py     # Email sending/receiving
├── calendar_integration.py  # Calendar scheduling
├── slack_integration.py     # Slack notifications
├── notion_integration.py    # Notion sync
├── airtable_integration.py  # Airtable storage
├── api_connectors.py        # Generic API connections
└── authentication.py        # OAuth/Auth handling
```

**Connected Services:**
- Email management
- Calendar events
- Slack notifications
- Notion database sync
- Airtable automation
- Custom APIs

---

### **`data_storage/` - Data Persistence**
Handles data storage backends.

```
data_storage/
├── database.py              # Main database interface
├── cache_manager.py         # Caching system
├── json_storage.py          # JSON file storage
├── csv_export.py            # CSV export functionality
├── schema.py                # Data schema definitions
└── migrations.py            # Database migrations
```

**Storage Types:**
- Relational database (SQL)
- JSON files
- CSV exports
- In-memory cache
- External integrations

---

### **`data/` - Data Assets**
Stores application data and resources.

```
data/
├── job_listings.csv         # Scraped job listings
├── applied_jobs.csv         # Applied job history
├── user_resume.txt          # User resume content
├── cover_letters/           # Generated cover letters
├── company_data.json        # Company information
└── user_profile.json        # User profile data
```

---

### **`analysis/` - Data Analysis & Reporting**
Analyzes job market and application performance.

```
analysis/
├── job_market_analyzer.py   # Job market insights
├── salary_analyzer.py       # Salary trend analysis
├── success_tracker.py       # Application success tracking
├── performance_reporter.py  # Performance metrics
├── trend_analyzer.py        # Trend identification
└── visualization.py         # Data visualization
```

**Analysis Areas:**
- Job market trends
- Salary analytics
- Application success rates
- Performance metrics
- Market insights

---

### **`tracking/` - Application Tracking**
Monitors job applications and interactions.

```
tracking/
├── application_tracker.py   # Track applications
├── interview_tracker.py     # Interview scheduling/tracking
├── connection_tracker.py    # LinkedIn connection tracking
├── follow_up_manager.py     # Follow-up scheduling
└── status_monitoring.py     # Application status updates
```

**Tracking Features:**
- Application status
- Interview scheduling
- Follow-up reminders
- Connection history
- Outcome tracking

---

### **`config/` & `config_and_setup/` - Configuration**
Manages application configuration.

```
config/
├── settings.py              # Main settings
├── credentials.py           # API credentials
├── environment.py           # Environment variables
└── constants.py             # Application constants

config_and_setup/
├── setup_wizard.py          # Initial setup wizard
├── config_validator.py      # Configuration validation
├── config_loader.py         # Dynamic configuration loading
└── requirements.txt         # Python dependencies
```

**Configuration:**
- Application settings
- API credentials (secure)
- Environment-specific configs
- Setup and initialization

---

### **`utils/` - Utility Functions**
Shared utilities and helper functions.

```
utils/
├── text_processing.py       # Text manipulation
├── date_utils.py            # Date/time utilities
├── string_utils.py          # String utilities
├── file_utils.py            # File operations
├── validators.py            # Input validation
├── logger.py                # Logging setup
└── decorators.py            # Custom decorators
```

**Utilities:**
- Text processing
- Date/time handling
- File operations
- Input validation
- Logging
- Common decorators

---

### **`scripts/` - Standalone Scripts**
Utility scripts for various tasks.

```
scripts/
├── database_setup.py        # Database initialization
├── data_import.py           # Bulk data import
├── cleanup.py               # Cleanup tasks
├── health_check.py          # System health checks
└── maintenance.py           # Maintenance tasks
```

---

### **`tests/` - Testing**
Test suite for the application.

```
tests/
├── test_scrapers.py         # Scraper tests
├── test_filters.py          # Filter tests
├── test_automation.py        # Automation workflow tests
├── test_integrations.py     # Integration tests
├── conftest.py              # Pytest configuration
└── fixtures.py              # Test fixtures
```

---

### **`deployment/` - Deployment Configuration**
Deployment and DevOps files.

```
deployment/
├── docker/                  # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── kubernetes/              # K8s manifests (if applicable)
├── cloud_config.yaml        # Cloud provider config
└── ci_cd.yml                # CI/CD pipeline config
```

---

### **`docs/` - Documentation**
Project documentation.

```
docs/
├── SETUP.md                 # Setup guide
├── USER_GUIDE.md            # User documentation
├── API_REFERENCE.md         # API documentation
├── ARCHITECTURE.md          # Architecture deep-dive
├── TROUBLESHOOTING.md       # Troubleshooting guide
└── CONTRIBUTING.md          # Contribution guidelines
```

---

### **`logs/` - Application Logs**
Runtime logs and debugging output.

```
logs/
├── app.log                  # Main application log
├── scraper.log              # Scraper operations
├── automation.log           # Automation workflow logs
├── error.log                # Error logs
└── debug/                   # Debug logs (if enabled)
```

---

### **`.github/` - GitHub Configuration**
GitHub-specific configuration.

```
.github/
├── workflows/
│   ├── tests.yml            # Automated testing
│   ├── deploy.yml           # Deployment workflow
│   └── lint.yml             # Code linting
└── ISSUE_TEMPLATE/          # Issue templates
```

---

## 🔄 Data Flow Diagram

```
Job Listings
    ↓
Scrapers → Raw Job Data
    ↓
Data Storage (CSV/JSON/DB)
    ↓
Filters & Analysis
    ↓
Matching & Ranking
    ↓
AI Processing (Resume, Cover Letter)
    ↓
Automation Engine
    ↓
Application Submission
    ↓
Tracking & Analytics
    ↓
Reporting & Insights
```

---

## 🔑 Key Module Dependencies

```
main.py
├── automation/job_hunter_workflow.py
├── scrapers/* (all scraper modules)
├── filters/* (all filter modules)
├── ai/* (AI processing modules)
├── integrations/* (external connections)
├── data_storage/* (persistence layer)
├── tracking/* (application tracking)
└── analysis/* (reporting & analytics)
```

---

## ⚙️ Common Workflows

### **1. Initial Setup**
```
setup_wizard.py → config_validator.py → database_setup.py → main.py
```

### **2. Job Hunting Cycle**
```
scrapers/* → data_storage → filters/* → ai/* → automation → tracking → analysis
```

### **3. Application Flow**
```
job_listing → resume_builder → cover_letter_generator → 
application_writer → automation_engine → email_integration → tracking
```

### **4. Analytics & Reporting**
```
tracking database → analysis/* → visualization → reporting
```

---

## 📦 External Dependencies

Key Python packages used:
- **Web Scraping:** BeautifulSoup, Selenium, Scrapy
- **Data Processing:** Pandas, NumPy
- **AI/ML:** OpenAI API, Hugging Face
- **Database:** SQLAlchemy, Psycopg2
- **Async:** asyncio, aiohttp
- **Testing:** pytest, unittest
- **Logging:** Python logging module

---

## 🚀 Running the Application

### **Quick Start**
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation
python main.py
```

### **With Specific Mode**
```bash
python main.py --mode scraping  # Run scraping only
python main.py --mode filtering # Run filtering only
python main.py --mode full      # Full pipeline
```

### **Testing**
```bash
pytest tests/
pytest tests/test_scrapers.py -v
```

---

## 📝 Configuration Reference

See `CONFIG_REFERENCE.py` for:
- API keys and credentials
- Filter thresholds
- Integration settings
- Database connection strings
- Logging configuration
- Deployment settings

---

## 🔐 Security Notes

- Store credentials in `.env` files (never commit sensitive data)
- Use environment variables for secrets
- Validate all external inputs
- Rate limit API calls
- Secure database connections

---

## 📊 Performance Optimization

- Parallel scraping with thread pools
- Caching frequently accessed data
- Database indexing on common queries
- Async I/O for network operations
- Batch processing for bulk operations

---

**Last Generated:** 2024
**Maintainer:** Your Name
**Status:** Production Ready

