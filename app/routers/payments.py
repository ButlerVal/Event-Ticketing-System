from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import secrets
from typing import cast

from .. import schemas, models
from ..database import get_db
from ..cruds import payments as payment_crud
from ..cruds import events as event_crud
from ..cruds import tickets as ticket_crud
from ..services import paystack, qr_service, email_service
from ..auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/initialize", response_model=schemas.PaymentResponse)
def initialize_payment(
    payment_data: schemas.PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Initialize payment with Paystack"""
    
    # Get event details
    event = event_crud.get_event(db, payment_data.event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    if int(getattr(event, "tickets_sold", 0) or 0) >= int(getattr(event, "capacity", 0) or 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event sold out")
    
    # Generate unique reference
    reference = f"TXN-{secrets.token_hex(16).upper()}"
    
    try:
        # Initialize Paystack payment
        response = paystack.initialize_payment(
            email=cast(str, getattr(current_user, "email", "")),
            amount=int(getattr(event, "price", 0) or 0),
            reference=reference
        )
        
        if response.get('status'):
            data = response.get('data', {})
            
            # Save payment record
            payment_crud.create_payment(
                db=db,
                user_id=int(getattr(current_user, "id", 0)),
                event_id=int(getattr(event, "id", 0)),
                reference=reference,
                amount=float(getattr(event, "price", 0.0) or 0.0),
                access_code=data.get('access_code', '')
            )
            
            return schemas.PaymentResponse(
                authorization_url=data.get('authorization_url'),
                reference=reference,
                access_code=data.get('access_code')
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment initialization failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Payment service unavailable: {str(e)}"
        )

@router.get("/verify/{reference}")
def verify_payment(
    reference: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Verify payment and generate ticket"""
    
    # Get payment record
    payment = payment_crud.get_payment_by_reference(db, reference)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    if cast(str, getattr(payment, "status", "")) == 'success':
        return {"message": "Payment already verified", "ticket_code": getattr(getattr(payment, "ticket", None), "ticket_code", None)}
    
    try:
        # Verify with Paystack
        response = paystack.verify_payment(reference)
        
        if response.get('status') and response.get('data', {}).get('status') == 'success':
            # Create ticket
            ticket = ticket_crud.create_ticket(
                db=db,
                user_id=int(getattr(current_user, "id", 0)),
                event_id=int(getattr(payment, "event_id", 0)),
                amount=float(getattr(payment, "amount", 0.0) or 0.0)
            )
            
            # Generate QR code
            qr_path = qr_service.generate_qr_code(cast(str, getattr(ticket, "ticket_code", "")))
            setattr(ticket, "qr_code_path", qr_path)
            db.commit()
            
            # Update payment status
            payment_crud.update_payment_status(db, reference, 'success', int(getattr(ticket, "id", 0)))
            
            # Update tickets sold
            event_crud.update_tickets_sold(db, int(getattr(payment, "event_id", 0)))
            
            # Send email
            event = event_crud.get_event(db, int(getattr(payment, "event_id", 0)))
            email_service.send_ticket_email(
                to_email=cast(str, getattr(current_user, "email", "")),
                user_name=cast(str, getattr(current_user, "name", "")),
                event_title=cast(str, getattr(event, "title", "")),
                ticket_code=cast(str, getattr(ticket, "ticket_code", "")),
                event_date=str(getattr(event, "event_date", "")),
                event_location=cast(str, getattr(event, "location", "")),
                qr_code_path=qr_path
            )
            
            return {
                "message": "Payment verified successfully",
                "ticket_code": getattr(ticket, "ticket_code"),
                "qr_code_path": qr_path
            }
        else:
            payment_crud.update_payment_status(db, reference, 'failed')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment verification failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Verification service unavailable: {str(e)}"
        )