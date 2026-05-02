"""
Sources router - status of each portal.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Source
from backend.schemas import SourceOut

router = APIRouter(tags=["Sources"])


@router.get("/sources/status", response_model=list[SourceOut])
def get_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@router.patch("/sources/{name}/toggle")
def toggle_source(name: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    src = db.query(Source).filter(Source.name == name).first()
    if not src:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    src.enabled = not src.enabled
    db.commit()
    return {"name": name, "enabled": src.enabled}
