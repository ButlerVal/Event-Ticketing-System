from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from .. import schemas
from ..database import get_db
from ..cruds import events as event_crud
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Create a new event (requires authentication)"""
    return event_crud.create_event(db, event, current_user.id)

@router.get("/", response_model=List[schemas.EventResponse])
def list_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all active events (public endpoint)"""
    return event_crud.get_events(db, skip, limit)

@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event details (public endpoint)"""
    event = event_crud.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event