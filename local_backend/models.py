"""
Local Emotion Detection Backend - Database Models

This module defines the SQLite database models for tracking video processing jobs.
This is a SEPARATE database from the Colab backend - they do not share data.

Job Status Flow:
    PENDING → PROCESSING → DONE
                        → FAILED
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os

# Database setup - uses SQLite for simplicity (local storage)
DATABASE_URL = "sqlite:///./local_backend.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class LocalJob(Base):
    """
    Database model for local emotion detection jobs.
    
    This is SEPARATE from the Colab backend's VideoJob model.
    Each job represents a video uploaded for LOCAL CPU processing.
    """
    __tablename__ = "local_jobs"

    # Primary key - UUID for unique identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Job status: PENDING, PROCESSING, DONE, FAILED
    status = Column(String(20), default="PENDING")
    
    # Human-readable status message
    status_message = Column(Text, default="Video uploaded. Waiting for processing to start.")
    
    # File paths (local filesystem)
    input_video_path = Column(String(500), nullable=True)
    output_video_path = Column(String(500), nullable=True)
    output_json_path = Column(String(500), nullable=True)
    
    # Progress tracking (0-100)
    progress = Column(String(10), default="0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert job to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "status": self.status,
            "status_message": self.status_message,
            "input_video_path": self.input_video_path,
            "output_video_path": self.output_video_path,
            "output_json_path": self.output_json_path,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ensure storage directories exist
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
INPUT_VIDEOS_DIR = os.path.join(STORAGE_DIR, "input_videos")
OUTPUT_VIDEOS_DIR = os.path.join(STORAGE_DIR, "output_videos")
OUTPUT_JSON_DIR = os.path.join(STORAGE_DIR, "output_json")
STATUS_DIR = os.path.join(STORAGE_DIR, "status")
TEMP_DIR = os.path.join(STORAGE_DIR, "temp")

for directory in [STORAGE_DIR, INPUT_VIDEOS_DIR, OUTPUT_VIDEOS_DIR, OUTPUT_JSON_DIR, STATUS_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)
