from sqlalchemy.orm import Session
from .. import models
from typing import Optional

def create_payment(
    db: Session,
    user_id: int,
    event_id: int,
    reference: str,
    amount: float,
    access_code: str
) -> models.Payment:
    db_payment = models.Payment(
        user_id=user_id,
        event_id=event_id,
        paystack_reference=reference,
        paystack_access_code=access_code,
        amount=amount,
        status='pending'
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_reference(db: Session, reference: str) -> Optional[models.Payment]:
    return db.query(models.Payment).filter(
        models.Payment.paystack_reference == reference
    ).first()

def update_payment_status(db: Session, reference: str, status: str, ticket_id: Optional[int] = None):
    payment = get_payment_by_reference(db, reference)
    if payment:
        setattr(payment, "status", status)
        if ticket_id is not None:
            setattr(payment, "ticket_id", ticket_id)
        db.commit()
        db.refresh(payment)
    return payment