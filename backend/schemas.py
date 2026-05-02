"""
Pydantic schemas for API validation.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    source: str
    title: str
    company: Optional[str] = None
    location_raw: Optional[str] = None
    department: Optional[str] = None
    province_or_city: Optional[str] = None
    modality: str = "no especificado"
    job_type: str = "no especificado"
    seniority: str = "no especificado"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "no especificado"
    salary_raw: Optional[str] = None
    publication_date_raw: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    functions: Optional[str] = None
    benefits: Optional[str] = None
    skills_detected: List[str] = Field(default_factory=list)
    career_area_detected: Optional[str] = None
    sector_detected: Optional[str] = None
    original_url: str
    status: str = "active"


class JobCreate(JobBase):
    source_job_id: Optional[str] = None
    confidence_score: float = 1.0


class JobOut(JobBase):
    id: str
    country: str = "Perú"
    district: Optional[str] = None
    education_required: Optional[str] = None
    experience_required: Optional[str] = None
    application_deadline: Optional[str] = None
    publication_date_estimated: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    confidence_score: float = 1.0
    duplicate_group_id: Optional[str] = None

    model_config = {"from_attributes": True}


class JobFilter(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    modality: Optional[str] = None
    job_type: Optional[str] = None
    seniority: Optional[str] = None
    career_area: Optional[str] = None
    source: Optional[str] = None
    date_range: Optional[str] = None  # "1d", "3d", "7d", "30d"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    page: int = 1
    page_size: int = 20


class SearchRequest(BaseModel):
    keyword: Optional[str] = None
    location: Optional[str] = None
    modality: Optional[str] = None
    job_type: Optional[str] = None
    seniority: Optional[str] = None
    career_area: Optional[str] = None
    sector: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    sources: List[str] = Field(default_factory=lambda: [
        "servir", "computrabajo", "bumeran", "laborum",
        "indeed", "getonboard", "jooble", "infojobs", "opcionempleo"
    ])
    max_pages: int = 1


class SourceOut(BaseModel):
    id: str
    name: str
    base_url: str
    enabled: bool
    last_scraped_at: Optional[datetime] = None
    last_status: str
    notes: Optional[str] = None
    job_count: int = 0

    model_config = {"from_attributes": True}


class SearchRunOut(BaseModel):
    id: str
    query: Optional[str] = None
    filters_json: Optional[Any] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    total_results: int = 0
    status: str
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedJobs(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    items: List[JobOut]
