import pandas as pd
from datetime import datetime, timezone
import sys
import os

# Ensure we can load from the database
try:
    from database.engine import engine
    from database.models import TrackedApplication
    from sqlalchemy.orm import Session
except ImportError:
    pass # Tests might skip this if paths are wrong

class ApplicationTracker:
    def __init__(self, tracker_file=None):
        # We ignore tracker_file now since we use SQLite, 
        # but keep the arg so existing code doesn't crash
        pass

    def get_tracked_links(self):
        """Return a set of links that have already been tracked."""
        try:
            with Session(engine) as db:
                links = db.query(TrackedApplication.link).all()
                return {row[0] for row in links}
        except Exception as e:
            print(f"Error loading tracker links from DB: {e}")
            return set()

    def log_jobs(self, df):
        if df.empty:
            return

        working = df.copy()

        # Schema alignment
        if "title" not in working.columns and "job_title" in working.columns:
            working["title"] = working["job_title"]
        if "link" not in working.columns and "apply_link" in working.columns:
            working["link"] = working["apply_link"]
            
        for column in ["role", "title", "company", "link"]:
            if column not in working.columns:
                working[column] = ""

        try:
            with Session(engine) as db:
                existing_links = {row[0] for row in db.query(TrackedApplication.link).all()}
                
                objects_to_add = []
                for _, row in working.iterrows():
                    link = row.get("link")
                    if not link or pd.isna(link) or link in existing_links:
                        continue
                        
                    tracked = TrackedApplication(
                        link=link,
                        title=str(row.get("title", ""))[:255] if not pd.isna(row.get("title")) else "",
                        company=str(row.get("company", ""))[:255] if not pd.isna(row.get("company")) else "",
                        role=str(row.get("role", ""))[:255] if not pd.isna(row.get("role")) else "",
                        status="scraped"
                    )
                    objects_to_add.append(tracked)
                    existing_links.add(link)
                    
                if objects_to_add:
                    db.bulk_save_objects(objects_to_add)
                    db.commit()
        except Exception as e:
            print(f"Failed to save tracked jobs to database: {e}")
