from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

import os

# Connect to SQLite database in the data/ directory (fallback securely)
db_path = Path(__file__).parent.parent / "data" / "job_hunter.db"
db_path.parent.mkdir(parents=True, exist_ok=True)

# Cloud Support Phase:
cloud_url = os.getenv("DATABASE_URL")
if cloud_url and cloud_url.startswith("postgres"):
    # SQLAlchemy requires postgresql:// instead of postgres://
    cloud_url = cloud_url.replace("postgres://", "postgresql://", 1)
    db_url = cloud_url
else:
    db_url = f"sqlite:///{db_path}"

# create_engine without echo so it doesn't flood logs unless debugging
engine = create_engine(db_url, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from database.models import Base
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
