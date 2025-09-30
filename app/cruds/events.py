from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional

def create_event(db: Session, event: schemas.EventCreate, user_id: int) -> models.Event:
    db_event = models.Event(
        **event.model_dump(),
        organizer_id=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.Event]:
    return db.query(models.Event).filter(
        models.Event.is_active == True
    ).offset(skip).limit(limit).all()

def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_active == True
    ).first()

def update_tickets_sold(db: Session, event_id: int, increment: int = 1) -> Optional[models.Event]:
    updated = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_active == True
    ).update(
        {models.Event.tickets_sold: models.Event.tickets_sold + increment},
        synchronize_session="fetch"
    )
    if updated:
        db.commit()
        return get_event(db, event_id)
    return None