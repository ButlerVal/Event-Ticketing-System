import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
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
    
    msg = MIMEMultipart()
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD
    if smtp_user is None or smtp_password is None:
        raise RuntimeError("SMTP_USER and SMTP_PASSWORD must be set in environment variables")

    msg['From'] = smtp_user
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
        with open(qr_code_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=ticket_{ticket_code}.png'
            )
            msg.attach(part)
    
    # Send email
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False