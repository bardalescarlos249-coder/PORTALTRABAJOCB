from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.models import Subscription

router = APIRouter(tags=["Subscriptions"])

class SubscriptionCreate(BaseModel):
    name: str
    email: str
    keyword: str
    frequency: str = "daily"

class SubscriptionUpdate(BaseModel):
    name: str = None
    email: str = None
    keyword: str = None
    frequency: str = None
    status: str = None

class SubscriptionOut(BaseModel):
    id: str
    name: str
    email: str
    keyword: str
    frequency: str
    status: str
    created_at: datetime
    last_sent_at: datetime = None

    class Config:
        from_attributes = True

@router.post("/subscriptions", response_model=SubscriptionOut)
def create_subscription(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    db_sub = Subscription(**sub.model_dump())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.get("/subscriptions", response_model=List[SubscriptionOut])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

@router.put("/subscriptions/{sub_id}", response_model=SubscriptionOut)
def update_subscription(sub_id: str, sub_update: SubscriptionUpdate, db: Session = Depends(get_db)):
    db_sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    update_data = sub_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sub, key, value)
        
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.delete("/subscriptions/{sub_id}")
def delete_subscription(sub_id: str, db: Session = Depends(get_db)):
    db_sub = db.query(Subscription).filter(Subscription.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(db_sub)
    db.commit()
    return {"message": "Deleted successfully"}
