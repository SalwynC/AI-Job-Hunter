from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class JobArchive(Base):
    """Stores all historically scraped jobs (Monthly Archive replacement)"""
    __tablename__ = 'job_archive'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    company: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=True)
    target_level: Mapped[str] = mapped_column(String, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    # Storing raw JSON string of full job data for backwards compatibility
    raw_data: Mapped[str] = mapped_column(Text, nullable=True) 
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class TrackedApplication(Base):
    """Tracks which jobs the user has already applied to or evaluated"""
    __tablename__ = 'tracked_applications'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    company: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="tracked") # tracked, applied, rejected, interviewed
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
