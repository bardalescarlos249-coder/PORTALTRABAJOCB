"""
Jobs router - listing, filtering, detail.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.database import get_db
from backend.models import Job
from backend.schemas import JobOut, PaginatedJobs

router = APIRouter(tags=["Jobs"])


def build_query(
    db: Session,
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    modality: Optional[str] = None,
    job_type: Optional[str] = None,
    seniority: Optional[str] = None,
    career_area: Optional[str] = None,
    source: Optional[str] = None,
    date_range: Optional[str] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
):
    q = db.query(Job)

    if keyword:
        kw = f"%{keyword.lower()}%"
        q = q.filter(
            or_(
                Job.title.ilike(kw),
                Job.company.ilike(kw),
                Job.description.ilike(kw),
                Job.requirements.ilike(kw),
            )
        )

    if location:
        loc = f"%{location.lower()}%"
        q = q.filter(
            or_(Job.location_raw.ilike(loc), Job.department.ilike(loc), Job.province_or_city.ilike(loc))
        )

    if modality and modality != "todos":
        q = q.filter(Job.modality.ilike(f"%{modality}%"))

    if job_type and job_type != "todos":
        q = q.filter(Job.job_type.ilike(f"%{job_type}%"))

    if seniority and seniority != "todos":
        q = q.filter(Job.seniority.ilike(f"%{seniority}%"))

    if career_area and career_area != "todos":
        q = q.filter(Job.career_area_detected.ilike(f"%{career_area}%"))

    if source and source != "todos":
        q = q.filter(Job.source.ilike(f"%{source}%"))

    if date_range:
        deltas = {"1d": 1, "3d": 3, "7d": 7, "30d": 30}
        days = deltas.get(date_range)
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            q = q.filter(Job.scraped_at >= cutoff)

    if salary_min is not None:
        q = q.filter(Job.salary_min >= salary_min)

    if salary_max is not None:
        q = q.filter(Job.salary_max <= salary_max)

    return q


@router.get("/jobs", response_model=PaginatedJobs)
def list_jobs(
    keyword: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    career_area: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    date_range: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None),
    salary_max: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = build_query(db, keyword, location, modality, job_type, seniority, career_area, source, date_range, salary_min, salary_max)
    total = q.count()
    items = q.order_by(Job.scraped_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size
    return PaginatedJobs(total=total, page=page, page_size=page_size, pages=pages, items=items)


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return job


@router.post("/jobs/deduplicate")
def deduplicate_jobs(db: Session = Depends(get_db)):
    from backend.normalizer.deduplicator import run_deduplication
    count = run_deduplication(db)
    return {"message": f"Deduplicación completada. {count} grupos encontrados."}
