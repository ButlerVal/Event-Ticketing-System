import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional
import logging
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_USER_EMAIL = os.getenv("SMTP_USER_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_ticket_email(
    to_email: str,
    user_name: str,
    event_title: str,
    ticket_code: str,
    event_date: str,
    event_location: str,
    qr_code_path: Optional[str] = None
):
    """Send ticket confirmation email with QR code"""
    
    # Validate SMTP configuration
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP credentials not configured")
        return False
    
    logger.info(f"Attempting to send email to {to_email}")
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER_EMAIL if SMTP_USER_EMAIL else "Event Tickets <onboarding@resend.dev>"
    msg['To'] = to_email
    msg['Subject'] = f"Your Ticket for {event_title}"
    
    # Email body
    body = f"""
Hi {user_name},

Thank you for your purchase! Here are your ticket details:

Event: {event_title}
Date: {event_date}
Location: {event_location}
Ticket Code: {ticket_code}

Please present the QR code attached to this email at the event entrance.

See you there!

Best regards,
Event Ticketing Team
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach QR code if provided
    if qr_code_path and os.path.exists(qr_code_path):
        try:
            with open(qr_code_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename=ticket_{ticket_code}.png'
                )
                msg.attach(part)
            logger.info(f"QR code attached: {qr_code_path}")
        except Exception as e:
            logger.error(f"Failed to attach QR code: {str(e)}")
    else:
        logger.warning(f"QR code not found at path: {qr_code_path}")
    
    # Send email
    try:
        logger.info(f"Connecting to SMTP server {SMTP_HOST}:{SMTP_PORT}")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            logger.info("SMTP connection secured with TLS")
            
            server.login(SMTP_USER, SMTP_PASSWORD)
            logger.info("SMTP login successful")
            
            server.send_message(msg)
            logger.info(f"Email sent successfully to {to_email}")
            
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}")
        logger.error("Check SMTP_USER and SMTP_PASSWORD in .env")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        return False