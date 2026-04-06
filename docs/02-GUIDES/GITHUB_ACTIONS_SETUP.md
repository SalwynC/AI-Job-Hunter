# 🚀 GitHub Actions Setup - Deploy to Cloud

**Goal:** Run your job scraper 24/7 for FREE using GitHub Actions  
**Setup Time:** 10 minutes  
**Cost:** $0/month

---

## Why GitHub Actions?

✅ **FREE** - 2000 minutes/month included (unlimited for public repos)  
✅ **Easy** - Simple YAML configuration  
✅ **Reliable** - Runs on GitHub's infrastructure  
✅ **Logs** - Full execution logs for debugging  
✅ **No server** - Think "serverless"  

---

## STEP 1: Create GitHub Repository

### 1.1 Push Your Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit: AI Job Hunter bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-job-hunter.git
git push -u origin main
```

### 1.2 Make Repository Public (Optional)
- Go to repository settings
- Set to Public (required for free GitHub Actions)
- This gives you unlimited minutes instead of 2000/month

---

## STEP 2: Add Secrets to GitHub

Secrets are encrypted environment variables that GitHub Actions uses securely.

### 2.1 Add Telegram Secrets
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `TELEGRAM_BOT_TOKEN`
   Value: Your bot token from @BotFather
5. Click **Add secret**

Repeat for:
- `TELEGRAM_CHAT_ID` - Your chat ID
- `GOOGLE_SHEETS_ID` - Your Google Sheets ID
- `GOOGLE_SHEETS_CREDENTIALS_JSON` - (see below)

### 2.2 Add Google Sheets Credentials
Your `credentials.json` needs to be added as a secret:

1. Open your `credentials.json` file locally
2. Copy the entire content
3. On GitHub: **New repository secret**
4. Name: `GOOGLE_SHEETS_CREDENTIALS_JSON`
5. Value: Paste the entire JSON content

**Important:** Never upload credentials.json to GitHub publicly!

---

## STEP 3: Create GitHub Workflow

### 3.1 Create Workflow File
1. Create directory: `.github/workflows/`
2. Create file: `.github/workflows/job-scraper.yml`
3. Paste the content below:

```yaml
name: AI Job Hunter - Automated Scraper

on:
  schedule:
    # Run every hour at the start of the hour
    - cron: '0 * * * *'
  
  # Allow manual trigger from GitHub UI
  workflow_dispatch:

jobs:
  scrape_jobs:
    runs-on: ubuntu-latest
    
    steps:
      # Check out repository code
      - name: Checkout code
        uses: actions/checkout@v3
      
      # Setup Python environment
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'
      
      # Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # Create credentials file from secret
      - name: Setup Google Sheets credentials
        run: |
          echo '${{ secrets.GOOGLE_SHEETS_CREDENTIALS_JSON }}' > credentials.json
      
      # Create .env file with secrets
      - name: Create .env file
        run: |
          cat > .env << EOF
          TELEGRAM_BOT_TOKEN=${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID=${{ secrets.TELEGRAM_CHAT_ID }}
          GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json
          GOOGLE_SHEETS_ID=${{ secrets.GOOGLE_SHEETS_ID }}
          RUN_PROFILE=hourly
          JOB_WINDOW=24h
          MAX_NOTIFY_JOBS=5
          LOG_LEVEL=INFO
          EOF
      
      # Run the job scraper
      - name: Run Job Scraper
        run: |
          python3 main.py
      
      # Upload logs as artifact (for debugging)
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: scraper-logs
          path: data/ci/
          retention-days: 7
      
      # Notify on failure
      - name: Send failure notification
        if: failure()
        run: |
          python3 << 'EOF'
          import os
          from telegram import Bot
          
          bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
          bot.send_message(
              chat_id=os.getenv('TELEGRAM_CHAT_ID'),
              text="❌ Job Scraper failed! Check GitHub Actions logs."
          )
          EOF
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

### 3.2 Workflow Explanation
- **Schedule**: Runs every hour (`0 * * * *`)
- **Manual trigger**: Can run from GitHub UI with "Run workflow"
- **Steps**: Checkout → Setup Python → Install deps → Get secrets → Run scraper
- **Logs**: Saved automatically (view in "Actions" tab)
- **Artifacts**: Last 7 days of logs kept for debugging

---

## STEP 4: Verify Workflow

### 4.1 Check Workflow File
1. Go to **Actions** tab in your GitHub repo
2. Look for "AI Job Hunter - Automated Scraper"
3. Should be enabled

### 4.2 Manually Trigger First Run
1. Click on the workflow
2. Click **Run workflow** dropdown
3. Select branch: **main**
4. Click **Run workflow**
5. Watch the execution in real-time

### 4.3 Check Execution
Click on the workflow run to see:
- ✅ Each step execution
- 📊 Time for each step  
- 📝 Full output logs
- 📦 Artifacts (logs)
- ❌ Errors if any

---

## STEP 5: Monitor Your Bot

### 5.1 Check Telegram Messages
Your Telegram chat should receive messages:
- Every hour with new jobs
- Message format: Job title + Company + Location + Link
- Google Sheets updated automatically

### 5.2 View GitHub Actions Logs
1. Go to **Actions** tab
2. Click on most recent run
3. Click on **"Run Job Scraper"** step
4. See detailed output

### 5.3 Check for Failures
If jobs don't arrive:
1. Go to Actions tab
2. Find the failed run (red ❌)
3. Click to see error details
4. Common issues:
   - Invalid token/credentials
   - Website down
   - Rate limiting
   - Missing .env variables

---

## Fine-Tuning the Schedule

### Different Frequencies

**Every hour:**
```yaml
- cron: '0 * * * *'
```

**Every 30 minutes:**
```yaml
- cron: '0,30 * * * *'
```

**Every 6 hours:**
```yaml
- cron: '0 0,6,12,18 * * *'
```

**Every day at 9 AM (UTC):**
```yaml
- cron: '0 9 * * *'
```

**Every weekday at 9 AM:**
```yaml
- cron: '0 9 * * 1-5'
```

**Note:** All times are UTC. Convert to your timezone!

---

## Advanced: Add Multiple Roles

To scrape for different job roles:

```yaml
jobs:
  scrape_data_analyst:
    runs-on: ubuntu-latest
    steps:
      # ... (same as above but with)
      - run: TARGET_ROLE=data_analyst python3 main.py
  
  scrape_software_engineer:
    runs-on: ubuntu-latest
    steps:
      # ... (same as above but with)
      - run: TARGET_ROLE=software_engineer python3 main.py
  
  scrape_mba:
    runs-on: ubuntu-latest
    steps:
      # ... (same as above but with)
      - run: TARGET_ROLE=mba python3 main.py
```

---

## Troubleshooting GitHub Actions

### Workflow Not Running
**Check:**
1. `.github/workflows/job-scraper.yml` exists
2. File is valid YAML (no tabs, proper indentation)
3. Branch is `main`

### Jobs Never Appear in Telegram
**Check:**
1. `TELEGRAM_BOT_TOKEN` secret is set correctly
2. `TELEGRAM_CHAT_ID` secret is set correctly
3. Check GitHub Actions logs for errors
4. Verify bot can send messages (run test manually)

### "Secrets not found" Error
**Fix:**
1. Go to Settings → Secrets → Actions
2. Verify all required secrets are present:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GOOGLE_SHEETS_ID`
   - `GOOGLE_SHEETS_CREDENTIALS_JSON`

### Python Dependencies Missing
**Fix:**
1. Make sure `requirements.txt` exists in project root
2. All packages listed (check line in workflow)

### Rate Limiting Issues
**Fix:**
1. Add delay between requests: `REQUEST_DELAY=5` in .env
2. Reduce scraping frequency (e.g., every 6 hours)
3. Use rotating proxies (advanced)

---

## Monitoring & Alerts

### Email Notifications
GitHub sends updates to your email:
- Workflow failures
- Successful runs (optional)

To enable:
1. Go to Settings
2. Notifications
3. Check "Workflows"

### Telegram Alerts
The workflow includes automatic failure alerts:
- Bot sends message on failure
- Includes error details

### View Logs
Latest 7 days of logs available:
1. Go to Actions
2. Click run
3. Click "Upload logs" artifact
4. Download `free_mode_last_run.log`

---

## Cost Breakdown

| Item | Free | Pro |
|------|------|-----|
| Minutes/month | 2000 | Unlimited |
| Storage | 500 MB | Unlimited |
| Data transfer | Unlimited | Unlimited |
| Concurrent jobs | 20 | 180 |
| **Cost** | **$0** | $21/month |

Your job = ~1-5 min per run × 24 runs/day = 24-120 min/month = **FREE tier covers this!**

---

## Next Steps

1. ✅ Create `.github/workflows/job-scraper.yml`
2. ✅ Add secrets to GitHub
3. ✅ Test workflow manually
4. ✅ Monitor Telegram for jobs
5. ✅ Adjust schedule as needed
6. ✅ Let it run 24/7

---

## Reference

- **GitHub Secrets:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Cron Syntax:** https://crontab.guru/
- **Actions Docs:** https://docs.github.com/en/actions
- **Workflow Syntax:** https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

---

**That's it!** Your bot is now running 24/7 in the cloud for FREE. 🚀
