"""
SQLAlchemy ORM models.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, Boolean, JSON
from backend.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=gen_uuid)
    source = Column(String, index=True, nullable=False)
    source_job_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location_raw = Column(String, nullable=True)
    country = Column(String, default="Perú")
    department = Column(String, nullable=True)
    province_or_city = Column(String, nullable=True)
    district = Column(String, nullable=True)
    modality = Column(String, default="no especificado")
    job_type = Column(String, default="no especificado")
    seniority = Column(String, default="no especificado")
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String, default="no especificado")
    salary_raw = Column(String, nullable=True)
    publication_date_raw = Column(String, nullable=True)
    publication_date_estimated = Column(DateTime, nullable=True)
    application_deadline = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    functions = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    education_required = Column(String, nullable=True)
    experience_required = Column(String, nullable=True)
    skills_detected = Column(JSON, default=list)
    career_area_detected = Column(String, nullable=True)
    sector_detected = Column(String, nullable=True)
    original_url = Column(String, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    confidence_score = Column(Float, default=1.0)
    duplicate_group_id = Column(String, nullable=True)

    class Config:
        from_attributes = True


class SearchRun(Base):
    __tablename__ = "search_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    query = Column(String, nullable=True)
    filters_json = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    total_results = Column(Integer, default=0)
    status = Column(String, default="running")
    error_message = Column(Text, nullable=True)


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime, nullable=True)
    last_status = Column(String, default="pending")
    notes = Column(Text, nullable=True)
    job_count = Column(Integer, default=0)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    frequency = Column(String, default="daily") # daily, weekly
    status = Column(String, default="active") # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sent_at = Column(DateTime, nullable=True)
