import re
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_L
from pyzbar.pyzbar import decode
from PIL import Image

def generate_qr_code(ticket_code: str) -> str:
    """Generate QR code for ticket, save it, and validate it can be decoded."""

    if not ticket_code or not isinstance(ticket_code, str):
        raise ValueError("ticket_code must be a non-empty string")

    # Clean filename
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', "_", ticket_code)

    # Ensure qr_codes directory exists
    qr_dir = Path("qr_codes")
    qr_dir.mkdir(parents=True, exist_ok=True)

    # Build QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(ticket_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save image safely
    filepath = qr_dir / f"{safe_name}.png"
    with filepath.open("wb") as f:
        img.save(f, "PNG")

    # ✅ Validate by reading QR back
    decoded = decode(Image.open(filepath))
    if not decoded or decoded[0].data.decode("utf-8") != ticket_code:
        raise ValueError(f"QR code for '{ticket_code}' was saved but could not be validated!")

    return str(filepath)
