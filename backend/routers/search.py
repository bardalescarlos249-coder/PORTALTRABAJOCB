"""
Search router - triggers scrapers across all 9 sources.
"""
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import SearchRun, Source
from backend.schemas import SearchRequest, SearchRunOut

router = APIRouter(tags=["Search"])

ALL_SOURCES = [
    "servir", "computrabajo", "bumeran", "laborum",
    "indeed", "getonboard", "jooble", "infojobs", "opcionempleo"
]


def get_scraper(name: str):
    """Dynamically load scraper class by name."""
    scrapers = {}
    mappings = {
        "servir": ("backend.scrapers.servir_scraper", "ServirScraper"),
        "computrabajo": ("backend.scrapers.computrabajo_scraper", "ComputrabajoScraper"),
        "bumeran": ("backend.scrapers.bumeran_scraper", "BumeranScraper"),
        "laborum": ("backend.scrapers.laborum_scraper", "LaborumScraper"),
        "indeed": ("backend.scrapers.indeed_scraper", "IndeedScraper"),
        "getonboard": ("backend.scrapers.getonboard_scraper", "GetonboardScraper"),
        "jooble": ("backend.scrapers.jooble_scraper", "JoobleScraper"),
        "infojobs": ("backend.scrapers.infojobs_scraper", "InfojobsScraper"),
        "opcionempleo": ("backend.scrapers.opcionempleo_scraper", "OpcionempleaScraper"),
    }
    if name not in mappings:
        return None
    module_path, class_name = mappings[name]
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except Exception:
        return None


def run_scraper_task(search_run_id: str, request_data: dict):
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        run = db.query(SearchRun).filter(SearchRun.id == search_run_id).first()
        total = 0
        errors = []

        sources = request_data.get("sources", ALL_SOURCES)

        for source_name in sources:
            ScraperClass = get_scraper(source_name)
            if not ScraperClass:
                continue

            source = db.query(Source).filter(Source.name == source_name).first()
            try:
                scraper = ScraperClass()
                filters = {
                    "keyword": request_data.get("keyword", ""),
                    "location": request_data.get("location", ""),
                    "modality": request_data.get("modality"),
                    "job_type": request_data.get("job_type"),
                    "seniority": request_data.get("seniority"),
                    "career_area": request_data.get("career_area"),
                    "sector": request_data.get("sector"),
                    "salary_min": request_data.get("salary_min"),
                    "salary_max": request_data.get("salary_max"),
                    "max_pages": request_data.get("max_pages", 1),
                }
                jobs = scraper.run(filters)
                scraper.save_results(jobs, db)
                total += len(jobs)

                if source:
                    source.last_scraped_at = datetime.utcnow()
                    source.last_status = "ok"
                    source.job_count = (source.job_count or 0) + len(jobs)
                    db.commit()

            except Exception as e:
                errors.append(f"{source_name}: {str(e)}")
                if source:
                    source.last_status = f"error: {str(e)[:100]}"
                    db.commit()

        if run:
            run.finished_at = datetime.utcnow()
            run.total_results = total
            run.status = "completed"
            if errors:
                run.error_message = " | ".join(errors)
            db.commit()

    except Exception as e:
        if run:
            run.status = "failed"
            run.error_message = str(e)
            run.finished_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/search", response_model=SearchRunOut)
def trigger_search(request: SearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run = SearchRun(
        query=request.keyword,
        filters_json=request.model_dump(),
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    background_tasks.add_task(run_scraper_task, run.id, request.model_dump())
    return run


@router.get("/search/runs", response_model=list[SearchRunOut])
def list_runs(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(SearchRun).order_by(SearchRun.started_at.desc()).limit(limit).all()

@router.get("/search/runs/{run_id}", response_model=SearchRunOut)
def get_run(run_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    run = db.query(SearchRun).filter(SearchRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/scrape/run", response_model=SearchRunOut)
def manual_scrape(request: SearchRequest, db: Session = Depends(get_db)):
    """Synchronous scraping - frontend waits for completion."""
    run = SearchRun(
        query=request.keyword,
        filters_json=request.model_dump(),
        status="running",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Run synchronously so frontend waits for results
    run_scraper_task(run.id, request.model_dump())

    db.refresh(run)
    return run


@router.get("/sources/available")
def list_available_sources():
    """Return all available scraper source names."""
    return {"sources": ALL_SOURCES}

