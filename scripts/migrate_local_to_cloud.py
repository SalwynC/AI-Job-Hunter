"""
Data Migration Script: SQLite Local to Cloud PostgreSQL
Run this script ONCE after setting up your DATABASE_URL in .env-analyst
to transfer all historical scraped jobs over to the cloud.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    cloud_url = os.getenv("DATABASE_URL")
    if not cloud_url:
        logger.error("❌ DATABASE_URL is not set. Please add it to your .env-analyst file.")
        return

    if cloud_url.startswith("postgres://"):
        cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)

    logger.info("Initializing Cloud Database...")
    
    # Needs the models to create tables
    from database.models import Base
    
    try:
        # Create Cloud Engine
        cloud_engine = create_engine(cloud_url, echo=False)
        Base.metadata.create_all(bind=cloud_engine)
        CloudSession = sessionmaker(bind=cloud_engine)
        logger.info("✅ Cloud Tables Verified/Created.")
        
        # Connect to Local SQLite
        from database.engine import engine as local_engine
        # Ensure the local doesn't accidentally pick up the cloud URL if engine.py was imported AFTER setting env
        from pathlib import Path
        db_path = Path(__file__).parent.parent / "data" / "job_hunter.db"
        local_sqlite = create_engine(f"sqlite:///{db_path}")
        LocalSession = sessionmaker(bind=local_sqlite)
        
        from database.models import JobArchive, TrackedApplication
        
        with LocalSession() as local_db, CloudSession() as cloud_db:
            # Migrate JobArchive
            local_jobs = local_db.query(JobArchive).all()
            logger.info(f"Preparing to migrate {len(local_jobs)} JobArchive records...")
            
            # Simple bulk merge (we don't preserve local specific primary keys if they clash, just migrate data)
            count = 0
            for job in local_jobs:
                # check if exists
                if not cloud_db.query(JobArchive).filter(JobArchive.link == job.link).first():
                    # Detach from local session manually 
                    db_obj = JobArchive(
                        link=job.link, title=job.title, company=job.company, location=job.location,
                        source=job.source, role=job.role, target_level=job.target_level,
                        raw_data=job.raw_data, scraped_at=job.scraped_at, score=job.score
                    )
                    cloud_db.add(db_obj)
                    count += 1
            cloud_db.commit()
            logger.info(f"✅ Successfully migrated {count} new jobs to the cloud!")
            
            # Migrate TrackedApplication
            local_tracked = local_db.query(TrackedApplication).all()
            logger.info(f"Preparing to migrate {len(local_tracked)} Tracked records...")
            
            count_t = 0
            for t in local_tracked:
                if not cloud_db.query(TrackedApplication).filter(TrackedApplication.link == t.link).first():
                    db_obj = TrackedApplication(
                        link=t.link, title=t.title, company=t.company, role=t.role,
                        status=t.status, timestamp=t.timestamp
                    )
                    cloud_db.add(db_obj)
                    count_t += 1
            cloud_db.commit()
            logger.info(f"✅ Successfully migrated {count_t} new tracked logs to the cloud!")
            
    except Exception as e:
        logger.error(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    migrate()
