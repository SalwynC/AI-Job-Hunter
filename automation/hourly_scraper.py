import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from analysis.gemini_scoring import score_jobs
from filters.final_filter import filter_jobs
from scrapers.common import scrape_jobs_for_profile
from tracking.application_tracker import ApplicationTracker
from automation.daily_storage import DailyStorage

logger = logging.getLogger(__name__)


class JobPipeline:
    def __init__(self, profile, run_profile="hourly", job_window="24h"):
        self.profile = profile
        self.run_profile = run_profile
        self.job_window = job_window
        self.data_dir = Path("data")
        self.output_dir = self.data_dir / profile["role_key"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = ApplicationTracker(self.data_dir / "tracking" / f"applications_{profile['role_key']}.csv")

    def run(self):
        jobs = scrape_jobs_for_profile(self.profile)
        if not jobs:
            logger.warning("No jobs were scraped for the current profile")
            return self.empty_result(0)

        # Early deduplication against history
        tracked_links = self.tracker.get_tracked_links()
        initial_count = len(jobs)
        jobs = [j for j in jobs if (j.get("link") or j.get("apply_link")) not in tracked_links]
        
        skipped = initial_count - len(jobs)
        if skipped > 0:
            logger.info(f"⏭️ Skipping {skipped} already tracked jobs")

        if not jobs:
            logger.info("No new jobs to process after deduplication")
            return self.empty_result(initial_count)

        df = pd.DataFrame(jobs)
        df = self.clean_jobs(df)
        df = score_jobs(df, self.profile)
        df = filter_jobs(df, self.profile)

        self.save_outputs(df)
        self.save_tracker(df)
        self.save_run_status(df)

        top_jobs = []
        if not df.empty:
            cols = ['title', 'company', 'link']
            if 'salary_text' in df.columns:
                cols.append('salary_text')
            top_df = df.head(5)[[c for c in cols if c in df.columns]]
            if 'salary_text' not in top_df.columns:
                top_df['salary_text'] = 'Not Disclosed'
            top_jobs = top_df.fillna('Unknown').to_dict('records')

        return {
            "role": self.profile["role_key"],
            "target_level": self.profile.get("target_level", "entry"),
            "scraped_jobs": initial_count,
            "new_jobs": len(df),
            "saved_jobs": len(df),
            "output_path": str(self.output_dir),
            "top_jobs": top_jobs
        }

    def empty_result(self, scraped_count):
        return {
            "role": self.profile["role_key"],
            "target_level": self.profile.get("target_level", "entry"),
            "scraped_jobs": scraped_count,
            "new_jobs": 0,
            "saved_jobs": 0,
            "output_path": str(self.output_dir),
        }

    def clean_jobs(self, df):
        if df.empty:
            return df

        df = df.drop_duplicates(subset=["link"], keep="first")
        df["title"] = df["title"].astype(str).str.strip()
        df["company"] = df["company"].astype(str).str.strip()
        df["location"] = df["location"].astype(str).str.strip()
        df["source"] = df["source"].astype(str).str.strip()
        df["role"] = self.profile["role_key"]
        df["target_level"] = self.profile.get("target_level", "entry")
        return df

    def save_outputs(self, df):
        csv_path = self.output_dir / "jobs.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df)} jobs to {csv_path}")

        summary_path = self.output_dir / "summary.json"
        with summary_path.open("w", encoding="utf-8") as fh:
            json.dump({"role": self.profile["role_key"], "saved_jobs": len(df)}, fh, indent=2)
        logger.info(f"Saved summary to {summary_path}")
        
        # Also save to daily storage and monthly archive
        DailyStorage.save_daily_jobs(df, self.profile["role_key"])
        DailyStorage.append_monthly_archive(df)

    def save_tracker(self, df):
        if df.empty:
            return
        self.tracker.log_jobs(df)

    def save_run_status(self, df):
        run_status = {
            "role": self.profile["role_key"],
            "run_profile": self.run_profile,
            "job_window": self.job_window,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "job_count": len(df),
            "output_path": str(self.output_dir / "jobs.csv"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        status_path = self.data_dir / "run_status_latest.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with status_path.open("w", encoding="utf-8") as fh:
            json.dump(run_status, fh, indent=2)
        logger.info(f"Saved run status to {status_path}")
