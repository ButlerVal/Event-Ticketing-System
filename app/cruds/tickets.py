from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional
import secrets

def generate_ticket_code() -> str:
    return f"TKT-{secrets.token_hex(8).upper()}"

def create_ticket(
    db: Session,
    user_id: int,
    event_id: int,
    amount: float
) -> models.Ticket:
    ticket_code = generate_ticket_code()
    
    db_ticket = models.Ticket(
        user_id=user_id,
        event_id=event_id,
        ticket_code=ticket_code,
        amount_paid=amount,
        status='active'
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_user_tickets(db: Session, user_id: int) -> List[models.Ticket]:
    return db.query(models.Ticket).filter(
        models.Ticket.user_id == user_id
    ).all()

def get_ticket_by_code(db: Session, ticket_code: str) -> Optional[models.Ticket]:
    return db.query(models.Ticket).filter(
        models.Ticket.ticket_code == ticket_code
    ).first()