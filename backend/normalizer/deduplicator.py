"""
Deduplication module using rapidfuzz for fuzzy matching.
"""
import logging
import uuid
from typing import List
from sqlalchemy.orm import Session
from backend.models import Job

logger = logging.getLogger(__name__)


def normalize_text(s: str) -> str:
    if not s:
        return ""
    return s.lower().strip()


def run_deduplication(db: Session) -> int:
    try:
        from rapidfuzz import fuzz
    except ImportError:
        logger.warning("rapidfuzz not installed, skipping deduplication")
        return 0

    jobs: List[Job] = db.query(Job).all()
    groups = {}
    assigned = set()
    count = 0

    for i, job_a in enumerate(jobs):
        if job_a.id in assigned:
            continue

        group_id = str(uuid.uuid4())
        group_jobs = [job_a]

        for j, job_b in enumerate(jobs):
            if i == j or job_b.id in assigned:
                continue

            title_sim = fuzz.ratio(normalize_text(job_a.title), normalize_text(job_b.title))
            company_sim = fuzz.ratio(normalize_text(job_a.company), normalize_text(job_b.company))

            if title_sim >= 85 and company_sim >= 75:
                group_jobs.append(job_b)

        if len(group_jobs) > 1:
            for gj in group_jobs:
                gj.duplicate_group_id = group_id
                assigned.add(gj.id)
            count += 1

    db.commit()
    return count
