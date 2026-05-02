"""
Export router - CSV, JSON, Excel.
"""
import io
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.models import Job

router = APIRouter(tags=["Export"])

EXPORT_COLUMNS = [
    "id", "source", "title", "company", "location_raw", "department",
    "province_or_city", "modality", "job_type", "seniority",
    "salary_min", "salary_max", "salary_currency", "salary_raw",
    "publication_date_raw", "description", "requirements", "functions",
    "benefits", "skills_detected", "career_area_detected", "sector_detected",
    "original_url", "scraped_at", "status",
]


def get_filtered_jobs(db: Session, keyword=None, source=None, location=None, modality=None):
    q = db.query(Job)
    if keyword:
        q = q.filter(Job.title.ilike(f"%{keyword}%"))
    if source and source != "todos":
        q = q.filter(Job.source == source)
    if location:
        q = q.filter(Job.location_raw.ilike(f"%{location}%"))
    if modality and modality != "todos":
        q = q.filter(Job.modality == modality)
    return q.order_by(Job.scraped_at.desc()).all()


@router.get("/export/csv")
def export_csv(
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    import csv
    jobs = get_filtered_jobs(db, keyword, source, location, modality)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for job in jobs:
        row = {col: getattr(job, col, "") for col in EXPORT_COLUMNS}
        if isinstance(row.get("skills_detected"), list):
            row["skills_detected"] = ", ".join(row["skills_detected"])
        if isinstance(row.get("scraped_at"), datetime):
            row["scraped_at"] = row["scraped_at"].isoformat()
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=ofertas_peru_{datetime.now().strftime('%Y%m%d')}.csv"},
    )


@router.get("/export/json")
def export_json(
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    jobs = get_filtered_jobs(db, keyword, source)
    result = []
    for job in jobs:
        row = {col: getattr(job, col, None) for col in EXPORT_COLUMNS}
        if isinstance(row.get("scraped_at"), datetime):
            row["scraped_at"] = row["scraped_at"].isoformat()
        result.append(row)
    content = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=ofertas_peru_{datetime.now().strftime('%Y%m%d')}.json"},
    )


@router.get("/export/excel")
def export_excel(
    keyword: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    import pandas as pd
    jobs = get_filtered_jobs(db, keyword, source)
    data = []
    for job in jobs:
        row = {col: getattr(job, col, None) for col in EXPORT_COLUMNS}
        if isinstance(row.get("skills_detected"), list):
            row["skills_detected"] = ", ".join(row["skills_detected"])
        data.append(row)
    df = pd.DataFrame(data, columns=EXPORT_COLUMNS)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ofertas")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ofertas_peru_{datetime.now().strftime('%Y%m%d')}.xlsx"},
    )
