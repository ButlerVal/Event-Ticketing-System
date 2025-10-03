import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_USER", "valbrilliantemporium@gmail.com")

def send_ticket_email(
    to_email: str,
    user_name: str,
    event_title: str,
    ticket_code: str,
    event_date: str,
    event_location: str,
    qr_code_path: Optional[str] = None
):
    """Send ticket confirmation email with QR code via SendGrid"""
    
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
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=f'Your Ticket for {event_title}',
        plain_text_content=body
    )
    
    # Attach QR code if provided
    if qr_code_path and os.path.exists(qr_code_path):
        with open(qr_code_path, 'rb') as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType('image/png')
        attachment.file_name = FileName(f'ticket_{ticket_code}.png')
        attachment.disposition = Disposition('attachment')
        message.attachment = attachment
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False