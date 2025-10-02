from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import secrets
import logging
from typing import cast, Any

from .. import schemas, models
from ..database import get_db
from ..cruds import payments as payment_crud
from ..cruds import events as event_crud
from ..cruds import tickets as ticket_crud
from ..services import paystack, qr_service, email_service
from ..auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)

@router.post("/initialize", response_model=schemas.PaymentResponse)
def initialize_payment(
    payment_data: schemas.PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Initialize payment with Paystack"""
    
    event = event_crud.get_event(db, payment_data.event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    # evaluate ORM attributes as native Python types for type checkers and runtime safety
    tickets_sold = cast(int, getattr(event, "tickets_sold"))
    capacity = cast(int, getattr(event, "capacity"))
    if tickets_sold >= capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event sold out")
    
    reference = f"TXN-{secrets.token_hex(16).upper()}"
    
    try:
        user_email = cast(str, getattr(current_user, "email"))
        event_price = cast(Any, getattr(event, "price"))
        response = paystack.initialize_payment(
            email=user_email,
            amount=int(event_price),
            reference=reference
        )
        
        if response.get('status'):
            data = response.get('data', {})
            
            payment_crud.create_payment(
                db=db,
                user_id=cast(int, getattr(current_user, "id")),
                event_id=cast(int, getattr(event, "id")),
                reference=reference,
                amount=float(event_price),
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
        logger.error(f"Payment initialization error: {str(e)}")
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
    
    payment = payment_crud.get_payment_by_reference(db, reference)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    # cast status to str to avoid SQLAlchemy boolean-expression comparisons
    if cast(str, getattr(payment, "status")) == 'success':
        ticket = getattr(payment, "ticket")
        return {
            "message": "Payment already verified",
            "ticket_code": ticket.ticket_code if ticket else None,
            "qr_code_path": ticket.qr_code_path if ticket else None
        }
    
    try:
        # Verify with Paystack
        response = paystack.verify_payment(reference)
        
        if response.get('status') and response.get('data', {}).get('status') == 'success':
            
            # Create ticket
            ticket = ticket_crud.create_ticket(
                db=db,
                user_id=cast(int, getattr(current_user, "id")),
                event_id=cast(int, getattr(payment, "event_id")),
                amount=float(cast(Any, getattr(payment, "amount")))
            )

            # Ensure ticket_code is always defined for later use
            ticket_code = cast(str, getattr(ticket, "ticket_code"))
            
            # Generate QR code
            try:
                qr_path = qr_service.generate_qr_code(ticket_code)
                # use setattr to avoid static typing on ORM attributes
                setattr(ticket, "qr_code_path", qr_path)
                db.commit()
                db.refresh(ticket)
                logger.info(f"QR code generated: {qr_path}")
            except Exception as qr_error:
                logger.error(f"QR code generation failed: {str(qr_error)}")
                # Continue even if QR fails
                qr_path = None
            
            # Update payment status
            payment_crud.update_payment_status(db, reference, 'success', cast(int, getattr(ticket, "id")))
            
            # Update tickets sold
            event_crud.update_tickets_sold(db, cast(int, getattr(payment, "event_id")))
            
            # Get event details for email
            event = event_crud.get_event(db, cast(int, getattr(payment, "event_id")))
            
            # Send email with error handling
            email_sent = False
            try:
                to_email = cast(str, getattr(current_user, "email"))
                user_name = cast(str, getattr(current_user, "name"))
                event_title = event.title if event else ""
                # ticket_code already set above
                event_date = str(event.event_date) if event else ""
                event_location = event.location if event else ""
    
                email_sent = email_service.send_ticket_email(
                    to_email=to_email,
                    user_name=user_name,
                    event_title=cast(str, event_title),
                    ticket_code=ticket_code,
                    event_date=cast(str, event_date),
                    event_location=cast(str, event_location),
                    qr_code_path=qr_path
                )
                
                if email_sent:
                    logger.info(f"Email sent successfully to {to_email}")
                else:
                    logger.error(f"Email failed to send to {to_email}")
                    # Don't fail the whole transaction if email fails
                    
            except Exception as email_error:
                logger.error(f"Email service error: {str(email_error)}")
                # Don't fail the transaction if email fails
            
            return {
                "message": "Payment verified successfully",
                "ticket_code": ticket_code,
                "qr_code_path": qr_path,
                "email_sent": email_sent
            }
        else:
            payment_crud.update_payment_status(db, reference, 'failed')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment verification failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Verification service unavailable: {str(e)}"
        )