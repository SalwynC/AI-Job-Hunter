"""
AI Job Hunter - Configuration Reference
Lists all settings and what they do
"""

# ============================================================================
# TELEGRAM SETTINGS - How to send job notifications
# ============================================================================

# Your Telegram personal chat ID
# Get it from: https://t.me/userinfobot
TELEGRAM_CHAT_ID = "6210886704"

# Bot token from @BotFather Telegram
# Used to send messages from bot to you
TELEGRAM_BOT_TOKEN = "8714057840:AAHMEuUS4A1tByxOrj55BTaog1hkkXLcOyk"

# Your Telegram API credentials
# Get from: https://my.telegram.org/apps
TELEGRAM_API_ID = "31092925"
TELEGRAM_API_HASH = "eaa313a7296497a11c0f496fb6583f0e"

# Which Telegram channels to scrape for jobs
TELEGRAM_CHANNELS = [
    "@jobsinindia",              # General jobs
    "@JOB_PORTAL_INDIA",         # General jobs
    "@jobs_for_freshers_2024",   # Freshers
    "@DataScienceJobs",          # Data roles
    "@DevOpsJobs",               # DevOps
    "@FullStackDeveloper",       # Full stack
    "@PythonDeveloperJobs",      # Python
    "@JavaDeveloperJobs",        # Java
    "@CloudComputingJobs",       # Cloud
    "@SoftwareEngineeringJobs",  # Software
    "@BackendDeveloperJobs",     # Backend
    "@FrontendDeveloperJobs",    # Frontend
    "@DataAnalystJobs",          # Data analyst
    "@BusinessAnalystJobs",      # Business analyst
    "@QATestingJobs",            # QA
    "@MLEngineeringJobs",        # ML
    "@ProductManagerJobs"        # Product manager
]

# ============================================================================
# JOB SEARCH SETTINGS - What to search for
# ============================================================================

# Which job sites to scrape (1=yes, 0=no)
ENABLE_NAUKRI = 1              # Naukri.com (largest India job site)
ENABLE_INTERNSHALA = 1         # Internshala.com (internships)
ENABLE_UNSTOP = 1             # Unstop.com (fellowships)
ENABLE_SHINE = 1              # Shine.com (premium)
ENABLE_TIMESJOBS = 1          # TimesJobs.com
ENABLE_FOUNDIT = 1            # Foundit.com (Indeed India)

# How many different job roles to search
# Current: 50+ roles (see .env-analyst for full list)
SEARCH_ROLES = [
    # Tech roles (20+)
    "Software Engineer", "Python Developer", "Java Developer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "Cloud Engineer", "QA Engineer",
    "Data Scientist", "Machine Learning Engineer", "AI Engineer",
    "Mobile Developer", "Android Developer", "iOS Developer",
    "Database Administrator", "Security Engineer", "Blockchain Developer",
    "Tech Lead", "Architect",
    
    # Business roles (10+)
    "Product Manager", "Business Analyst", "Data Analyst",
    "Sales Executive", "Sales Engineer", "Project Manager",
    "HR Executive", "Finance Executive", "Operations Manager",
    
    # Creative roles (5+)
    "UI/UX Designer", "Graphic Designer", "Content Writer",
    "Technical Writer", "Trainer",
    
    # Other roles (10+)
    "Intern", "Graduate Trainee", "Fresher", "Entry Level",
    # ... and more
]

# Also search for internships (not just jobs)
JOB_TYPE = ["Job", "Internship"]

# How recent should jobs be (in days)
JOB_WINDOW_DAYS = 2  # Jobs posted in last 2 days

# Location to search
LOCATION_PRIMARY = "India"
LOCATION_SECONDARY = "Remote"

# Experience level filter
EXPERIENCE_LEVEL = "0-2 years"  # Freshers and early career

# ============================================================================
# SCHEDULING SETTINGS - When and how often to search
# ============================================================================

# How often to scrape for jobs (in minutes)
# Lower = more frequent updates, but more API calls
# 5 = every 5 minutes (288 times per day)
# 30 = every 30 minutes (48 times per day)
SCRAPE_INTERVAL_MINUTES = 5

# Maximum number of retries if scraping fails
MAX_RETRIES = 3

# Maximum jobs to process in one cycle
MAX_JOBS_PER_CYCLE = 40

# For background scheduling (optional)
AUTOPILOT_INTERVAL_SECONDS = 1800  # 30 minutes
BACKGROUND_RUN_INTERVAL_MINUTES = 30

# Enable 24/7 continuous operation
ENABLE_BACKGROUND_RUNNER = 1

# ============================================================================
# DELIVERY SETTINGS - What gets sent to you
# ============================================================================

# Maximum jobs to send per notification
MAX_NOTIFY_JOBS = 40

# Send all jobs or just top matches
NOTIFY_SCOPE = "all"  # or "top", "scored"

# Send to Telegram automatically
ENABLE_TELEGRAM_NOTIFICATIONS = 1

# Auto digest settings
ENABLE_AUTO_DIGEST = 1
AUTO_DIGEST_MORNING_TIME = "08:00"   # 8 AM digest
AUTO_DIGEST_EVENING_TIME = "18:00"   # 6 PM digest
AUTO_DIGEST_WINDOW_HOURS = 24        # Last 24 hours

# ============================================================================
# DATA QUALITY SETTINGS - Ensure real, useful jobs
# ============================================================================

# Only show real jobs (no fake/demo data)
VERIFY_REAL_DATA_ONLY = 1

# Don't use mock jobs as fallback
ALLOW_MOCK_FALLBACK = 0

# Hard block - never show mock Telegram jobs
ALLOW_MOCK_TELEGRAM_JOBS = 0

# Data source verification
DATA_SOURCE = "REAL ONLY"

# ============================================================================
# SCORING & FILTERING - Intelligent job matching
# ============================================================================

# Enable skill-based scoring
ENABLE_INTELLIGENT_SCORING = 1

# Apply score threshold (0-10)
# Higher = stricter filtering
ANALYST_SCORE_APPLY_TODAY = 6.5

# Review score threshold
ANALYST_SCORE_REVIEW = 5.0

# Safe filtering mode (don't miss good jobs)
SAFE_FILTER_MODE = 1

# Daily target minimum
DAILY_TARGET_MIN_JOBS = 300

# ============================================================================
# FEATURES - Optional features
# ============================================================================

# Track applications you've made
ENABLE_APPLICATION_TRACKING = 1

# Export to Excel
ENABLE_EXCEL_EXPORT = 1

# AI analysis of jobs (experimental)
ENABLE_CLAUDE_HANDOFF = 0

# Google Sheets integration
ENABLE_GOOGLE_SHEETS = 0  # Requires setup

# ============================================================================
# GOOGLE SHEETS CONFIG - If using Google Sheets export
# ============================================================================

SHEETS_DAILY_JOBS_TAB = "Daily_Jobs"
SHEETS_TOP_JOBS_TAB = "Top_Jobs"
SHEETS_INSIGHTS_TAB = "Insights"
SHEETS_APPLICATIONS_TAB = "Applications"

# ============================================================================
# DEPLOYMENT - Cloud settings
# ============================================================================

# When running on cloud (Render/Railway)
# Services use environment variables instead of .env file

CLOUD_PLATFORM = "Render"  # or "Railway", "GitHub Actions"
CLOUD_MONITOR_FILE = "logs/cloud_run.log"

# ============================================================================
# LOGGING - Debug information
# ============================================================================

LOG_LEVEL = "INFO"  # INFO, DEBUG, WARNING, ERROR
LOG_FILE = "logs/app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# HINTS FOR CUSTOMIZATION
# ============================================================================

# WANT MORE JOBS?
# - Reduce SCRAPE_INTERVAL_MINUTES (e.g., 2 instead of 5)
# - Add more SEARCH_ROLES
# - Enable all job platforms (set all ENABLE_* to 1)

# WANT FEWER JOBS?
# - Increase SCRAPE_INTERVAL_MINUTES (e.g., 30 instead of 5)
# - Be more specific with SEARCH_ROLES
# - Increase ANALYST_SCORE_APPLY_TODAY threshold

# CHANGE JOB ROLES?
# - Edit SEARCH_ROLES list in .env-analyst
# - Redeploy to cloud
# - Takes effect immediately

# CHANGE FREQUENCY?
# - Edit SCRAPE_INTERVAL_MINUTES in .env-analyst
# - Redeploy to cloud
# - Some changes may take 5-10 minutes to apply

# NOT GETTING JOBS?
# - Check all ENABLE_* platforms are 1
# - Check Telegram credentials are correct
# - Check logs for errors
# - Try reducing ANALYZER_SCORE_* thresholds
# - Try adding more SEARCH_ROLES

# ============================================================================
# QUICK MODIFICATIONS
# ============================================================================

# To get jobs about specific technology:
# Add to SEARCH_ROLES: "Rust Developer", "Go Developer", "PHP Developer"

# To focus on specific roles:
# SEARCH_ROLES = ["Frontend Developer", "Backend Developer", "Full Stack Developer"]
# SCRAPE_INTERVAL_MINUTES = 2  # More frequent for focused search

# To get more internships:
# ENABLE_INTERNSHALA = 1  (already enabled)
# May need to adjust thresholds

# To get only remote jobs:
# LOCATION_PRIMARY = "Remote"
# LOCATION_SECONDARY = "India"
