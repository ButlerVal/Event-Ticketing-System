import qrcode
from qrcode.constants import ERROR_CORRECT_L
from io import BytesIO
import os
from pathlib import Path

def generate_qr_code(ticket_code: str) -> str:
    """Generate QR code for ticket and return file path"""
    
    # Create QR code directory if it doesn't exist
    qr_dir = Path("qr_codes")
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(ticket_code)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file using an in-memory buffer then write bytes to the Path
    filename = f"{ticket_code}.png"
    filepath = qr_dir / filename
    # Use BytesIO to avoid passing Path directly to image.save (type-checkers and some PIL stubs)
    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    filepath.write_bytes(buffer.getvalue())
    
    return str(filepath)