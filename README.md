# AI Job Hunter

Automated job discovery pipeline built for continuous cloud operation.

## What this project does

- Scrapes jobs from web sources (Naukri, Internshala, Unstop, Shine, TimesJobs)
- Ingests Telegram channel jobs when Telegram API credentials are configured
- Deduplicates and validates jobs before saving
- Sends Telegram summaries for each completed cycle
- Supports role-aware filtering through profile configuration

## Core entrypoints

- `python main.py`
  - Runs the role-aware pipeline flow
  - Best when you want profile-driven filtering and scoring

- `python job_scraper_3hr.py`
  - Runs continuous scheduler loop
  - Best for unattended operation

- `python job_scraper_3hr.py --once`
  - Runs one complete scrape/notify cycle and exits
  - Used by GitHub Actions scheduled workflow

## Current structure

- `main.py`: role-aware pipeline entrypoint
- `job_scraper_3hr.py`: continuous scheduler/orchestrator
- `automation/`: pipeline orchestration logic
- `config/`: profile and runtime config loader
- `roles/role_profiles.yaml`: role definitions
- `scrapers/`: source scrapers, processor, and shared helpers
- `data_storage/`: generated CSV output
- `logs/`: runtime logs
- `docs/`: operational notes and setup docs

## Cloud-first 24/7 setup

Use GitHub Actions (no laptop required):

1. Push this repository to GitHub.
2. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - Optional: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`
3. Confirm workflow exists at:
   - `.github/workflows/ai-job-hunter.yml`
4. Let scheduled runs execute automatically.

The workflow runs `python job_scraper_3hr.py --once` on a schedule.

## Local verification commands

```bash
cd ai-job-automation
pip install -r requirements.txt
python3 job_scraper_3hr.py --once
python3 main.py
```

## Environment notes

Main environment file used in this project:

- `.env-analyst`

Key variables:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SCRAPE_INTERVAL_MINUTES`
- Role/profile related variables used by `config/role_loader.py`

## Troubleshooting

- If Telegram notifications fail:
  - Check token/chat ID secrets and bot permissions.
- If no jobs are returned:
  - Check scraper source availability and filters.
- If scheduler appears locked:
  - Remove stale lock file in `data/` and rerun.

## Status

Runtime path validated for:

- `job_scraper_3hr.py --once`
- `main.py`

Both execute successfully with current structure.