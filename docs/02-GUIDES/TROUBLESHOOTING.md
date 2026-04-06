# 🔧 TROUBLESHOOTING GUIDE - AI Job Hunter Issues & Fixes

---

## ❌ COMMON ISSUES & SOLUTIONS

### **Issue 1: No jobs received on Telegram**

**Symptoms:**
- Created deployment but no job messages appear
- Waited 10+ minutes but nothing shows up

**Checklist (In Order):**

1. **Is your cloud service running?**
   ```
   ✓ Go to Render dashboard
   ✓ Click your service
   ✓ Should say "Live" in green
   ✓ If not, click "Manual Deploy"
   ```

2. **Are Telegram credentials correct?**
   ```
   ✓ TELEGRAM_BOT_TOKEN must start with: 8714057840:
   ✓ TELEGRAM_CHAT_ID must be a long number: 6210886704
   ✓ TELEGRAM_API_ID must be: 31092925
   ✓ Copy from .env-analyst, paste in Render exactly
   ```

3. **Check the logs:**
   ```
   ✓ Go to Render dashboard → Logs tab
   ✓ Look for: "✅ Cycle complete" or "Found XX jobs"
   ✓ Look for errors: "❌" or "ERROR"
   ```

**If you see errors in logs:**

| Error Message | Fix |
|---------------|-----|
| `"Missing environment variable"` | Check Render env vars match .env-analyst exactly |
| `"Cannot import job_scraper_3hr"` | Ensure file exists in GitHub repo |
| `"Telegram token invalid"` | Get new token from @BotFather |
| `"CHAT_ID error"` | Get ID from @userinfobot and verify it's set |
| `"No jobs found"` | Wait 15-20 minutes (first run is slow) |

---

### **Issue 2: Same jobs appearing multiple times**

**Symptoms:**
- See the same job notification 2-3 times in a row
- Department duplicate jobs

**What's Happening:**
- Deduplication is working, but may have a cache issue

**Fix:**

**Option A: Wait (Usually fixes itself)**
```
After 24 hours, old jobs drop out automatically
Just wait - don't panic
```

**Option B: Clear Cache (Nuclear option)**
```
1. In Render dashboard, go to "Environment"
2. Add: DISABLE_CACHE=1
3. Click "Redeploy"
4. Wait 2 minutes
5. Remove the flag and redeploy again
```

**Option C: Manual Local Fix**
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation
rm -f data/jobs_seen.json  # Delete cache file
git add .
git commit -m "Clear job cache"
git push
# Redeploy from Render
```

---

### **Issue 3: "Too many jobs" - Overwhelming notifications**

**Symptoms:**
- Getting 200+ job messages at once
- Telegram chat flooded with notifications

**Fixes (Choose One):**

**Fix 1: Reduce Frequency** (Recommended)
```
1. Go to Render Environment variables
2. Change: SCRAPE_INTERVAL_MINUTES = 30 (instead of 5)
3. Click Save
4. Redeploy
5. Now runs every 30 min instead of every 5
```

**Fix 2: Reduce Max Jobs Per Cycle**
```
1. Set: MAX_NOTIFY_JOBS = 20 (instead of 40)
2. Redeploy
```

**Fix 3: Reduce Job Roles**
```
1. Edit .env-analyst
2. Keep only roles you want:
   "Software Engineer,Python Developer,Data Analyst"
3. Push to GitHub
4. Redeploy
```

---

### **Issue 4: Jobs are too generic / not relevant**

**Symptoms:**
- Filtering is too loose
- Getting jobs that don't match your profile

**Fixes:**

**1. Be More Specific with Roles:**
```bash
# Instead of 50 roles, search for specific ones:
export SEARCH_ROLES='Python Developer,Backend Developer,Full Stack Developer'
```

**2. Increase Filtering Threshold:**
```
In .env-analyst, increase:
ANALYST_SCORE_APPLY_TODAY=7.5  (was 6.5)
# Higher threshold = fewer but better jobs
```

**3. Change Experience Level:**
```
export EXPERIENCE_LEVEL='2-5 years'
# or '5+ years' if you want senior roles
```

---

### **Issue 5: Want internships specifically, not jobs**

**Symptoms:**
- Mostly seeing job postings, not internships
- Internshala isn't showing up

**Fixes:**

**Option A: Focus on Internship Platform**
```bash
export ENABLE_INTERNSHALA=1     # Internship focused ✅
export ENABLE_NAUKRI=0          # Turn off naukri
export ENABLE_UNSTOP=1          # Good for fellowships
export ENABLE_SHINE=0           # Turn off (jobs focused)
export SCRAPE_INTERVAL_MINUTES=2  # More frequent
```

**Option B: Add "Internship" to roles explicitly**
```bash
export SEARCH_ROLES='Data Analyst Internship,Python Developer Internship,Frontend Developer Internship'
```

**Option C: Set job type**
```bash
export JOB_TYPE='Internship'  # Only internships
# (was Job,Internship)
```

---

### **Issue 6: Getting "example.com" or fake links**

**Symptoms:**
- Apply links lead to example.com
- Clicking apply doesn't work

**Status:** ✅ **FIXED in latest version**

**If still happening:**
```bash
1. Update .env-analyst (pull latest)
2. Ensure: ALLOW_MOCK_TELEGRAM_JOBS=0
3. Redeploy
4. Check logs for validation messages
```

---

### **Issue 7: Cloud service keeps stopping/restarting**

**Symptoms:**
- Service shows "Build Failed" or "Stopped"
- Keeps restarting every few minutes

**Probable Causes & Fixes:**

**Cause 1: Missing Python packages**
```
Fix: Check requirements.txt has all packages
pip install -r requirements.txt
Ensure python-telegram-bot is listed
git push to update repo
Redeploy
```

**Cause 2: Memory limit exceeded**
```
Fix in Render:
1. Go to service settings
2. Increase memory (if on free tier, consider Railway)
3. Or reduce MAX_JOBS_PER_CYCLE=20
```

**Cause 3: Timeout on startup**
```
Fix:
1. Render > Settings > Health Check
2. Disable health checks (or increase timeout)
3. Or change Start Command to just: python cloud_run.py
```

---

### **Issue 8: Want to add custom job platforms**

**Symptoms:**
- Want to scrape from another website
- Current platforms don't have what you need

**How to add (Advanced):**

```python
# 1. Create new file: scrapers/custom_scraper.py
def scrape_custom_site(role):
    # Your scraping code here
    return jobs_list

# 2. In scrapers/common.py, add:
from scrapers.custom_scraper import scrape_custom_site

# 3. Enable via env var:
export ENABLE_CUSTOM=1
```

**Easier alternative:** Use the generic Telegram channel scraper - you can add any job channel:
```bash
export TELEGRAM_CHANNELS='...,@your_custom_job_channel'
```

---

## ✅ VERIFICATION CHECKLIST

**Before claiming "it's working":**

- [ ] Telegram bot configuration
  - [ ] Bot token valid (test with @BotFather)
  - [ ] Chat ID verified (test with @userinfobot)
  - [ ] Received at least 1 test message

- [ ] Job sources
  - [ ] At least one platform enabled
  - [ ] Platform is accessible (no network blocks)
  - [ ] No anti-scraping blocks

- [ ] Environment variables
  - [ ] All vars set in Render (not just locally)
  - [ ] No typos in var names
  - [ ] No extra spaces in values

- [ ] Cloud deployment
  - [ ] Service shows "Live" status
  - [ ] No errors in logs
  - [ ] Logs update every 5 minutes

- [ ] Job output
  - [ ] Getting at least 5+ jobs per cycle
  - [ ] Jobs have valid links (https://)
  - [ ] No duplicate links

---

## 🔍 HOW TO READ LOGS (Render Dashboard)

**Go to:** Render Dashboard → Your Service → Logs

**What to look for:**

```
✅ GOOD SIGNS:
- "🤖 Starting AI Job Hunter"
- "✅ All environment variables verified"
- "📍 Starting job scraper cycle"
- "✅ Scraping cycle complete!"
- "Found 25 jobs"
- "✅ CYCLE SUCCESSFUL"

❌ BAD SIGNS:
- "ERROR" or "Exception"
- "Missing environment variable"
- "Cannot import"
- "Timeout"
- "ConnectionError"
- Service keeps restarting
```

---

## 📞 ADVANCED DEBUGGING

**Enable Debug Mode (For detailed logs):**

```
In Render Environment:
LOG_LEVEL=DEBUG

Then check logs - more verbose output
```

**Check Python version compatibility:**
```bash
# Locally:
python3 --version
# Should be 3.8 or higher

# Check in Render logs for Python version
```

**Test locally before deploying:**
```bash
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation
python3 cloud_run.py
# Should complete in <1 minute
# Should see logs in console
```

---

## 🚨 EMERGENCY RECOVERY

**If everything broke:**

1. **Stop the service:**
   - Render → Service → Suspend Service

2. **Reset environment:**
   ```bash
   git checkout .env-analyst  # Reset to original
   git pull  # Get latest
   ```

3. **Redeploy from scratch:**
   - Delete service in Render
   - Create new service
   - Follow QUICK_START.md steps again

4. **Still broken?**
   - Check GitHub issues
   - Review COMPLETE_SOLUTION_GUIDE.md
   - Try different cloud platform (Railway instead of Render)

---

## 🎯 QUICK FIXES BY TIME

**Problem just appeared? Try this based on when it happened:**

| Time Since Deploy | Most Likely Issue | Quick Fix |
|-------------------|-------------------|-----------|
| 0-5 minutes | Still starting up | Wait 5 more minutes |
| 5-15 minutes | Env vars not set | Check Render env vars |
| 15-60 minutes | First cycle running | Wait (first run slow) |
| 1-6 hours | Jobs depleted, cache building | Normal, wait |
| 6-24 hours | Performance issue | Reduce SCRAPE_INTERVAL_MINUTES |
| 24+ hours | Persistent problem | Check version, redeploy |

---

## 📊 PERFORMANCE EXPECTATIONS

**Normal operation looks like:**

```
Cycle 1 (5:00):  Found 35 jobs → Sent 35
Cycle 2 (5:05):  Found 28 jobs → Sent 28 (some duplicates removed)
Cycle 3 (5:10):  Found 32 jobs → Sent 31 (duplicates removed)
...
Cycle 100 (8:20): Found 22 jobs → Sent 20 (higher filtering)
```

**This is NORMAL** - not failure.

---

## 💡 STILL STUCK?

**Provide these details and I can help:**

1. Screenshot of Render logs (last 50 lines)
2. Your SEARCH_ROLES (what you're searching for)
3. Which platforms you enabled
4. How long has it been running
5. Exact error message(s) if any

**Then I'll fix it!**
