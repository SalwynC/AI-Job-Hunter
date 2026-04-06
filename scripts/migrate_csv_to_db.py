import json
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

# Add parent directory to path so we can import internal modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import JobArchive, TrackedApplication
from database.engine import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"

def migrate_monthly_archives(db: Session):
    monthly_dir = DATA_DIR / "monthly"
    if not monthly_dir.exists():
        logger.info("No monthly directory found.")
        return

    csv_files = list(monthly_dir.glob("monthly_*_full.csv"))
    if not csv_files:
        logger.info("No monthly archives to migrate.")
        return

    total_added = 0
    
    # Pre-fetch existing links to avoid dup warnings
    existing_links = {row[0] for row in db.query(JobArchive.link).all()}

    for f in csv_files:
        logger.info(f"Processing archive: {f.name}")
        df = pd.read_csv(f)
        
        objects_to_add = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            link = row_dict.get("link")
            if not link or pd.isna(link) or link in existing_links:
                continue
                
            job = JobArchive(
                link=link,
                title=row_dict.get("title", ""),
                company=row_dict.get("company", ""),
                location=row_dict.get("location", ""),
                source=row_dict.get("source", ""),
                role=row_dict.get("role", ""),
                target_level=row_dict.get("target_level", ""),
                score=float(row_dict.get("score", 0.0)) if not pd.isna(row_dict.get("score")) else 0.0,
                raw_data=json.dumps(row_dict)
            )
            objects_to_add.append(job)
            existing_links.add(link)
            
        if objects_to_add:
            db.bulk_save_objects(objects_to_add)
            db.commit()
            total_added += len(objects_to_add)
            logger.info(f"Added {len(objects_to_add)} jobs from {f.name}")

    logger.info(f"Migrated {total_added} total jobs into JobArchive.")

def migrate_tracking_files(db: Session):
    tracking_dir = DATA_DIR / "tracking"
    if not tracking_dir.exists():
        logger.info("No tracking directory found.")
        return

    csv_files = list(tracking_dir.glob("applications*.csv"))
    if not csv_files:
        logger.info("No tracking files to migrate.")
        return

    total_added = 0
    existing_links = {row[0] for row in db.query(TrackedApplication.link).all()}

    for f in csv_files:
        logger.info(f"Processing tracking file: {f.name}")
        try:
            df = pd.read_csv(f)
        except Exception as e:
            logger.error(f"Could not read {f.name}: {e}")
            continue
            
        objects_to_add = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            link = row_dict.get("link")
            if not link or pd.isna(link) or link in existing_links:
                continue
                
            tracked = TrackedApplication(
                link=link,
                title=row_dict.get("title", ""),
                company=row_dict.get("company", ""),
                role=row_dict.get("role", ""),
                status="tracked"
            )
            objects_to_add.append(tracked)
            existing_links.add(link)
            
        if objects_to_add:
            db.bulk_save_objects(objects_to_add)
            db.commit()
            total_added += len(objects_to_add)
            logger.info(f"Added {len(objects_to_add)} tracked items from {f.name}")

    logger.info(f"Migrated {total_added} total tracked applications.")

def main():
    logger.info("Initializing database...")
    init_db()
    
    with Session(engine) as db:
        migrate_monthly_archives(db)
        migrate_tracking_files(db)
        
    logger.info("Migration Complete!")

if __name__ == "__main__":
    main()
