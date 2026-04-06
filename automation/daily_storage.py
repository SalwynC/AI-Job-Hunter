"""
Enhanced Daily Storage System for AI Job Hunter
Handles date-based file organization, monthly archiving, and metadata
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DailyStorage:
    """
    Organize job data by date with multiple levels:
    - Daily: jobs_2026-04-05.csv
    - Role-specific: jobs_2026-04-05_data_analyst.csv
    - Monthly archive: monthly_2026_04_full.csv (append-only)
    - Metadata: summary_2026-04-05.json
    """

    BASE_PATH = Path(__file__).parent.parent / "data"

    @staticmethod
    def get_daily_dir(date: Optional[datetime] = None) -> Path:
        """Get directory for specified date (default: today UTC)."""
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        daily_dir = DailyStorage.BASE_PATH / "daily" / date_str
        daily_dir.mkdir(parents=True, exist_ok=True)
        return daily_dir

    @staticmethod
    def get_monthly_dir(date: Optional[datetime] = None) -> Path:
        """Get directory for monthly archive."""
        if date is None:
            date = datetime.utcnow()
        
        monthly_dir = DailyStorage.BASE_PATH / "monthly"
        monthly_dir.mkdir(parents=True, exist_ok=True)
        return monthly_dir

    @staticmethod
    def save_daily_jobs(
        df: pd.DataFrame,
        role: str,
        date: Optional[datetime] = None
    ) -> Path:
        """
        Save daily jobs to: data/daily/2026-04-05/jobs_2026-04-05_data_analyst.csv
        
        Args:
            df: DataFrame with jobs
            role: Role/profile name (e.g., 'data_analyst')
            date: Date (default: today)
            
        Returns:
            Path to saved file
        """
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        daily_dir = DailyStorage.get_daily_dir(date)
        
        filename = f"jobs_{date_str}_{role}.csv"
        filepath = daily_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"💾 Saved daily jobs: {filepath} ({len(df)} jobs)")
        
        return filepath

    @staticmethod
    def save_daily_all_jobs(
        df: pd.DataFrame,
        date: Optional[datetime] = None
    ) -> Path:
        """
        Save all jobs for the day (across all roles):
        data/daily/2026-04-05/jobs_2026-04-05.csv
        """
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        daily_dir = DailyStorage.get_daily_dir(date)
        
        filename = f"jobs_{date_str}.csv"
        filepath = daily_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"💾 Saved all daily jobs: {filepath} ({len(df)} jobs)")
        
        return filepath

    @staticmethod
    def append_monthly_archive(
        df: pd.DataFrame,
        date: Optional[datetime] = None
    ) -> Optional[Path]:
        """
        Append to historical DB archive (replaces old monthly archive):
        data/job_hunter.db -> job_archive table
        
        Handles deduplication by URL efficiently to prevent OOM.
        """
        if df.empty:
            return None

        try:
            import json
            from database.engine import engine
            from database.models import JobArchive
            from sqlalchemy.orm import Session
            
            with Session(engine) as db:
                existing_links = {row[0] for row in db.query(JobArchive.link).all()}
                
                objects_to_add = []
                for _, row in df.iterrows():
                    row_dict = row.to_dict()
                    link = row_dict.get("link")
                    if not link or pd.isna(link) or link in existing_links:
                        continue
                        
                    job = JobArchive(
                        link=link,
                        title=str(row_dict.get("title", ""))[:255] if not pd.isna(row_dict.get("title")) else "",
                        company=str(row_dict.get("company", ""))[:255] if not pd.isna(row_dict.get("company")) else "",
                        location=str(row_dict.get("location", ""))[:255] if not pd.isna(row_dict.get("location")) else "",
                        source=str(row_dict.get("source", ""))[:255] if not pd.isna(row_dict.get("source")) else "",
                        role=str(row_dict.get("role", ""))[:255] if not pd.isna(row_dict.get("role")) else "",
                        target_level=str(row_dict.get("target_level", ""))[:255] if not pd.isna(row_dict.get("target_level")) else "",
                        score=float(row_dict.get("score", 0.0)) if not pd.isna(row_dict.get("score")) else 0.0,
                        raw_data=json.dumps(row_dict)
                    )
                    objects_to_add.append(job)
                    existing_links.add(link)
                    
                if objects_to_add:
                    db.bulk_save_objects(objects_to_add)
                    db.commit()
                    logger.info(
                        f"📦 Appended {len(objects_to_add)} new jobs to database archive"
                    )
                else:
                    logger.info("📦 No new jobs to add to database archive")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to append to database archive: {e}")
            return None

    @staticmethod
    def save_execution_summary(
        stats: Dict[str, Any],
        date: Optional[datetime] = None
    ) -> Path:
        """
        Save execution metadata:
        data/daily/2026-04-05/summary_2026-04-05.json
        """
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        daily_dir = DailyStorage.get_daily_dir(date)
        
        filename = f"summary_{date_str}.json"
        filepath = daily_dir / filename
        
        summary = {
            "date": date_str,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **stats  # Merge in provided stats
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Saved execution summary: {filename}")
        return filepath

    @staticmethod
    def save_source_metrics(
        metrics: Dict[str, Any],
        date: Optional[datetime] = None
    ) -> Path:
        """
        Save per-source scraping metrics:
        data/daily/2026-04-05/sources_2026-04-05.json
        """
        if date is None:
            date = datetime.utcnow()
        
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        daily_dir = DailyStorage.get_daily_dir(date)
        
        filename = f"sources_{date_str}.json"
        filepath = daily_dir / filename
        
        data = {
            "date": date_str,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sources": metrics
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Saved source metrics: {filename}")
        return filepath

    @staticmethod
    def get_latest_daily_file(role: Optional[str] = None) -> Optional[Path]:
        """Get the latest daily jobs file (for latest role or all)."""
        daily_dir = DailyStorage.BASE_PATH / "daily"
        
        if not daily_dir.exists():
            return None
        
        # Get all daily directories, sort by date descending
        date_dirs = sorted([d for d in daily_dir.iterdir() if d.is_dir()], reverse=True)
        
        if not date_dirs:
            return None
        
        latest_date_dir = date_dirs[0]
        
        if role:
            # Look for role-specific file
            pattern = f"jobs_*_{role}.csv"
        else:
            # Look for all-roles file
            pattern = "jobs_*.csv"
        
        files = list(latest_date_dir.glob(pattern))
        
        return files[0] if files else None

    @staticmethod
    def cleanup_old_files(days_to_keep: int = 30) -> int:
        """
        Clean up daily files older than N days.
        Keep monthly archives forever.
        Returns number of deleted files.
        """
        daily_dir = DailyStorage.BASE_PATH / "daily"
        
        if not daily_dir.exists():
            return 0
        
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for date_dir in daily_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            try:
                dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                
                if dir_date < cutoff_date:
                    # Delete directory and contents
                    import shutil
                    shutil.rmtree(date_dir)
                    deleted_count += 1
                    logger.info(f"🗑️  Deleted old daily directory: {date_dir.name}")
            except ValueError:
                # Directory name doesn't match date format, skip
                pass
        
        return deleted_count


class ExecutionMetrics:
    """Track execution statistics and health metrics."""
    
    @staticmethod
    def log_execution(
        role: str,
        scraped_count: int,
        filtered_count: int,
        execution_time_sec: float,
        sources_used: List[str],
        success_count: int,
        total_sources: int,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Log execution to: data/tracking/executions.csv"""
        
        if date is None:
            date = datetime.utcnow()
        
        tracking_dir = DailyStorage.BASE_PATH / "tracking"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        success_rate = (success_count / total_sources * 100) if total_sources > 0 else 0
        
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "date": (date if isinstance(date, datetime) else pd.to_datetime(date)).strftime("%Y-%m-%d"),
            "role": role,
            "jobs_scraped": scraped_count,
            "jobs_filtered": filtered_count,
            "execution_time_sec": round(execution_time_sec, 2),
            "sources_used": ",".join(sources_used),
            "success_count": success_count,
            "total_sources": total_sources,
            "success_rate_percent": round(success_rate, 1),
        }
        
        filepath = tracking_dir / "executions.csv"
        
        if filepath.exists():
            existing_df = pd.read_csv(filepath)
            combined_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
            combined_df.to_csv(filepath, index=False)
        else:
            pd.DataFrame([record]).to_csv(filepath, index=False)
        
        logger.info(f"📈 Logged execution metrics for role '{role}'")
        return record
