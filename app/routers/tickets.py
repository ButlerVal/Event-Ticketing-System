from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, cast

from .. import schemas
from ..database import get_db
from ..cruds import tickets as ticket_crud
from ..auth import get_current_user
from .. import models

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/my-tickets", response_model=List[schemas.TicketResponse])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all tickets for current user"""
    return ticket_crud.get_user_tickets(db, cast(int, current_user.id))

@router.get("/{ticket_code}", response_model=schemas.TicketResponse)
def get_ticket(ticket_code: str, db: Session = Depends(get_db)):
    """Get ticket by code (public for verification)"""
    ticket = ticket_crud.get_ticket_by_code(db, ticket_code)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket