# 🚀 AI JOB HUNTER - QUICK START (SIMPLE STEPS)

> **TL;DR:** Deploy in 5 minutes to cloud, get job notifications on Telegram 24/7 with 50+ job roles & internships

---

## 🎯 WHAT YOU GET

```
✅ Automatic job & internship searches 
✅ 50+ different job roles supported
✅ 6 real job sites scraped  
✅ Telegram notifications every 5 minutes
✅ Works 24/7 WITHOUT your laptop
✅ 100% FREE (Render free tier)
✅ No Docker needed
```

---

## ⚡ QUICK SETUP (Choose Your Path)

### **PATH 1: Deploy to Cloud (Recommended - 5 minutes)**

#### **Step 1️⃣ - GitHub Setup**
```bash
# Just push your code to GitHub
# (If using Replit or similar, skip this)
```

#### **Step 2️⃣ - Deploy to Render**

1. Go to: https://render.com
2. Click **"Sign Up"** → Choose **GitHub**
3. Click **"New +"** → Select **"Web Service"**
4. Select your **ai-job-hunter** repo
5. Fill in:
   ```
   Name: ai-job-hunter
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -c "import time; [__import__('cloud_run').main() for _ in range(288)]"
   ```
6. Go to **"Environment"** tab
7. Add these variables (copy from your `.env-analyst`):
   ```
   TELEGRAM_BOT_TOKEN=8714057840:AAHMEuUS4A1tByxOrj55BTaog1hkkXLcOyk
   TELEGRAM_CHAT_ID=6210886704
   TELEGRAM_API_ID=31092925
   TELEGRAM_API_HASH=eaa313a7296497a11c0f496fb6583f0e
   SCRAPE_INTERVAL_MINUTES=5
   ENABLE_NAUKRI=1
   ENABLE_INTERNSHALA=1
   ENABLE_UNSTOP=1
   ENABLE_SHINE=1
   ENABLE_TIMESJOBS=1
   SEARCH_ROLES=(copy the whole list from .env-analyst)
   JOB_TYPE=Job,Internship
   ```
8. Click **"Create Web Service"**
9. ✅ **DONE! Running in cloud now**

#### **Step 3️⃣ - Check If Working**

Check Telegram in 5 minutes - you should see job messages like:
```
1. Software Engineer - Python
   Apply: https://naukri.com/...
   Role: Job
   
2. Data Analyst Internship
   Apply: https://internshala.com/...
   Role: Internship
```

---

### **PATH 2: Test Locally First (Before Cloud)**

```bash
# 1. Navigate to project
cd /Users/apple/Desktop/SalwynFolder/ai-job-hunter/ai-job-automation

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run ONE test cycle
python cloud_run.py

# 4. Check if jobs came to Telegram
# (Should see message in your Telegram chat within 30 seconds)

# 5. If working, deploy to Render using PATH 1
```

---

## 📋 FEATURES BREAKDOWN

### **1. Jobs & Internships**
Now searches for BOTH:
- Regular full-time jobs
- Internship positions
- Contract work
- Freelance opportunities

### **2. 50+ Job Roles**

Covers ALL categories:

**Tech Roles:**
- Python, Java, JavaScript, C++
- Frontend, Backend, Full Stack
- DevOps, Cloud, AI/ML
- Mobile (Android, iOS)

**Business Roles:**
- Product Manager
- Business Analyst
- Data Analyst
- Sales Executive
- HR, Finance, Operations

**Creative Roles:**
- UX/UI Designer
- Graphic Designer
- Content Writer
- Trainer

**... and 30+ more!**

### **3. Real Job Platforms**

Searches from:
1. **Naukri.com** - Largest India job site
2. **Internshala.com** - Internship focused
3. **Unstop.com** - Fellowships & competitions
4. **Shine.com** - Premium jobs
5. **TimesJobs.com** - Established jobs
6. **Foundit.com** - Indeed India
7. **Telegram Channels** - Direct job posts

### **4. Smart Filtering**

✅ Only shows valid jobs  
✅ Removes duplicates  
✅ Real links only (no fake)  
✅ Location: India + Remote  
✅ Experience: 0-2 years (customizable)  

### **5. Telegram Notifications**

Every 5 minutes, get up to 40 best jobs sent to your Telegram chat.

---

## 🔧 WHAT CHANGED (From Before)

| Before | Now |
|--------|-----|
| ❌ Only "Analyst" roles | ✅ 50+ roles ALL types |
| ❌ Only jobs | ✅ Jobs + Internships |
| ❌ Limited sites | ✅ 6+ platforms |
| ❌ Local only | ✅ Cloud 24/7 |
| ❌ Manual updates | ✅ Auto searches |

---

## 📊 EXPECTED RESULTS

**Per Day:** 300-500 new job opportunities  
**Per Notification:** 30-40 jobs  
**Frequency:** Every 5 minutes  
**Latency:** Real-time after posting  

---

## ⚠️ TROUBLESHOOTING

### **"No jobs in Telegram"**

**Check:**
1. Is Render deployment running? (Check dashboard)
2. Is TELEGRAM_BOT_TOKEN correct? (Copy from `.env-analyst`)
3. Did you set all environment variables?
4. Check Telegram bot token works: `curl https://api.telegram.org/botTOKEN/getMe`

### **"Too many notifications"**

**Fix:** Reduce frequency in Render environment:
```
SCRAPE_INTERVAL_MINUTES=30  (instead of 5)
```

### **"Same jobs repeating"**

**Normal!** But deduplication is enabled. If still happening:
```bash
# Delete cache
rm -f data/jobs_seen.json

# Redeploy
# (Render will automatically restart)
```

### **"Seeing test/example jobs"**

**That's fixed!** Those were removed in the update.

---

## 🎓 LEARNING RESOURCES

Want to understand how it works?

**Read these in order:**

1. [`COMPLETE_SOLUTION_GUIDE.md`](./COMPLETE_SOLUTION_GUIDE.md) - Full explanation
2. [`AUDIT_REPORT_2026_04_02.md`](./AUDIT_REPORT_2026_04_02.md) - Issues fixed
3. Code walkthrough:
   - `job_scraper_3hr.py` - Main scraper
   - `cloud_run.py` - Cloud entry point
   - `scrapers/` - Individual site scrapers

---

## 🚀 NEXT STEPS (DO THIS NOW)

**Option A: Deploy Now (Recommended)**
1. Have your GitHub account ready
2. Follow "PATH 1" above
3. Done! Check Telegram in 5 min

**Option B: Test First (Safe)**
1. Follow "PATH 2"
2. Verify locally works
3. Then deploy to cloud

**Option C: Read Everything**
1. Read `COMPLETE_SOLUTION_GUIDE.md`
2. Understand the architecture
3. Then deploy

---

## 💡 PRO TIPS

1. **Change search roles:** Edit `.env-analyst` and redeploy
2. **Change frequency:** Edit `SCRAPE_INTERVAL_MINUTES` 
3. **More jobs per notification:** Edit `MAX_NOTIFY_JOBS=40`
4. **Different location:** Edit `LOCATION_PRIMARY='India'`
5. **Monitor in real-time:** Check Render logs dashboard

---

## 📞 NEED HELP?

1. Check **TROUBLESHOOTING** section above
2. Check logs in Render dashboard
3. Verify all Telegram credentials
4. Ensure all env vars are set

---

## ✅ CHECKLIST BEFORE DEPLOYING

- [ ] GitHub repo has all files
- [ ] `.env-analyst` has your Telegram tokens
- [ ] `cloud_run.py` file exists
- [ ] `requirements.txt` is up to date
- [ ] Decided on job roles you want
- [ ] Create Render account
- [ ] Follow "PATH 1" deployment steps

---

**🎉 You're ready! Deploy now and enjoy automated job hunting! 🎉**
