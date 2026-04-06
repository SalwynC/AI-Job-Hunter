# ✅ AI JOB HUNTER - SETUP CHECKLIST

**Status:** Getting your system ready for 24/7 automated job hunting  
**Estimated Time:** 30 minutes for setup + credentials

---

## STEP 1: TELEGRAM BOT SETUP (5 minutes)

### 1.1 Create Telegram Bot
1. Open Telegram and search for **@BotFather**
2. Send `/start` command
3. Send `/newbot` command
4. Choose a name for your bot (e.g., "MyJobHunter")
5. Choose a username (e.g., "MyJobHunterBot")
6. **Copy the API token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
7. Send `/setcommands` to BotFather and add these commands:
   ```
   start - Start the bot
   status - Check current jobs
   settings - Configure preferences
   ```

### 1.2 Get Your Chat ID
1. Start a new chat with your bot
2. Send any message
3. Paste this URL in your browser (replace TOKEN with your bot token):
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
4. Look for `"chat":{"id": XXXXX}` - that's your **Chat ID**
5. Save both TOKEN and CHAT ID

### 1.3 Add Bot to Your Group (Optional)
- If you want job notifications in a group chat:
  1. Create a new Telegram group
  2. Add your bot to the group
  3. Use the group's chat ID instead

---

## STEP 2: GOOGLE SHEETS SETUP (10 minutes)

### 2.1 Create GCP Project
1. Go to: https://console.cloud.google.com
2. Click **Select a Project** → **New Project**
3. Name it: "AIJobHunter"
4. Click **Create**

### 2.2 Enable Google Sheets API
1. Go to: https://console.cloud.google.com/apis/dashboard
2. Click **+ ENABLE APIS AND SERVICES**
3. Search for **Google Sheets API**
4. Click it and press **ENABLE**

### 2.3 Create Service Account
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **+ CREATE SERVICE ACCOUNT**
3. Name: "job-hunter-bot"
4. Description: "AI Job Hunter automation service"
5. Click **Create and Continue**
6. Grant role: **Editor**
7. Click **Continue** → **Done**

### 2.4 Create & Download API Key
1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON**
5. Click **Create** - file downloads automatically
6. **Important:** Save this file safely in your project as `credentials.json`
7. Copy the **service account email** (looks like: `job-hunter-bot@project-id.iam.gserviceaccount.com`)

### 2.5 Create Google Sheet
1. Go to: https://sheets.google.com
2. Click **+ New** to create blank spreadsheet
3. Name it: **"AI Job Hunter - Jobs"**
4. Share this sheet with your service account email:
   - Click **Share**
   - Paste the service account email
   - Grant **Editor** access
   - Send

5. The sheet ID is in the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
6. Copy and save **SHEET_ID**

---

## STEP 3: CREATE .env FILE (5 minutes)

1. In your project root, create a file called `.env` (duplicate `.env.template`)
2. Fill in with your values:

```env
# From Telegram Bot setup
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_get_updates

# From Google Sheets setup
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEETS_ID=your_sheet_id_from_url

# Your preferences
TARGET_ROLE=data_analyst
RUN_PROFILE=hourly
JOB_WINDOW=24h
MAX_NOTIFY_JOBS=5
```

3. **IMPORTANT:** Add `.env` to `.gitignore` (don't share credentials!)

---

## STEP 4: SETUP LOCAL ENVIRONMENT (10 minutes)

### 4.1 Install Python Dependencies
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import telegram; import gspread; import pandas; print('✅ All dependencies installed')"
```

### 4.2 Place Credentials File
```bash
# Copy your downloaded credentials.json to the project root
cp /path/to/your/downloaded/credentials.json ./credentials.json

# Verify it exists
ls -la credentials.json
```

### 4.3 Test Configuration Loading
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation

python3 << 'EOF'
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Check required variables
required = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
    'GOOGLE_SHEETS_ID'
]

for var in required:
    value = os.getenv(var)
    if value:
        masked = value[:10] + '...' if len(value) > 10 else value
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: MISSING - Please add to .env file")

print("\nConfiguration check complete!")
EOF
```

---

## STEP 5: TEST EACH COMPONENT (15 minutes)

### 5.1 Test Telegram Connection
```bash
python3 << 'EOF'
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

try:
    bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
    me = bot.get_me()
    print(f"✅ Telegram bot connected: @{me.username}")
except Exception as e:
    print(f"❌ Telegram connection failed: {e}")
EOF
```

### 5.2 Test Google Sheets Connection
```bash
python3 << 'EOF'
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

try:
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'credentials.json')
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    print("✅ Google Sheets connection successful")
except Exception as e:
    print(f"❌ Google Sheets connection failed: {e}")
EOF
```

### 5.3 Test Data Pipeline
```bash
# This will run a test scrape (takes 2-5 minutes)
python3 << 'EOF'
import sys
from config.role_loader import load_role_profile
from automation.hourly_scraper import JobPipeline

role = load_role_profile("data_analyst")
pipeline = JobPipeline(role, run_profile="test", job_window="24h")
result = pipeline.run()

print(f"✅ Pipeline test complete:")
print(f"   - Role: {result['role']}")
print(f"   - Jobs scraped: {result['scraped_jobs']}")
print(f"   - Jobs saved: {result['saved_jobs']}")
EOF
```

---

## STEP 6: RUN YOUR FIRST AUTOMATED JOB HUNT (5 minutes)

### Option A: Run Manually (For Testing)
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation
python3 main.py
```

You should see:
- ✅ Jobs scraped from multiple websites
- ✅ Results saved to `data/data_analyst/jobs.csv`
- ✅ Telegram message sent with job summary
- ✅ Google Sheets updated with job data

### Option B: Schedule with GitHub Actions (For 24/7)
See: `GITHUB_ACTIONS_SETUP.md`

---

## ✅ VERIFICATION CHECKLIST

After setup, you should have:

- [ ] `.env` file created with all required variables
- [ ] `credentials.json` placed in project root
- [ ] Python dependencies installed
- [ ] ✅ Telegram bot token verified
- [ ] ✅ Google Sheets access verified
- [ ] ✅ First job scrape completed successfully
- [ ] ✅ Telegram message received with job results
- [ ] ✅ Google Sheets updated with job data
- [ ] ✅ No errors in logs

---

## 🆘 TROUBLESHOOTING

### Issue: "TELEGRAM_BOT_TOKEN not found"
- **Solution:** Make sure `.env` file exists and `TELEGRAM_BOT_TOKEN=...` is set
- **Check:** `cat .env | grep TELEGRAM_BOT_TOKEN`

### Issue: "Google Sheets authentication failed"
- **Solution:** Verify `credentials.json` path is correct
- **Check:** `ls -la credentials.json` should show the file

### Issue: "Telegram message not sending"
- **Solution:** Check if bot has permission to send messages to chat
- **Fix:** 
  1. Go back to chat with your bot
  2. Send `/start` again
  3. Check that chat ID matches `TELEGRAM_CHAT_ID`

### Issue: "Scrapers returning no jobs"
- **Solution:** Check internet connection and website accessibility
- **Fix:**
  ```bash
  # Test single scraper
  python3 << 'EOF'
  from scrapers.naukri_scraper import scrape_naukri_jobs
  from config.role_loader import load_role_profile
  
  role = load_role_profile("data_analyst")
  jobs = scrape_naukri_jobs(role)
  print(f"Found {len(jobs)} jobs")
  EOF
  ```

### Issue: Rate limiting (429 errors)
- **Solution:** Add delays between requests
- **Fix:** Update `.env`: `REQUEST_DELAY=5`

---

## 📚 NEXT STEPS

Once verification is complete:

1. **Phase 1 Complete:** Local system working
2. **Phase 2:** Test all 9 websites (LinkedIn, Naukri, etc.)
3. **Phase 3:** Implement AI-based job filtering
4. **Phase 4:** Deploy to cloud (GitHub Actions)
5. **Phase 5:** Organize documentation and project structure
6. **Phase 6:** Final testing and production launch

---

## 📞 SUPPORT

If you get stuck:
1. Check `TROUBLESHOOTING.md`
2. Look at logs in `data/ci/` directory
3. Review `.env` file for missing variables

**Ready to start Phase 1?** Run the test steps above!
