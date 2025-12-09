import io

from PIL import Image
import pytesseract
from pytesseract import TesseractNotFoundError

# Point directly to the exe (same as test_ocr.py)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_file(content: bytes) -> str:
    image = Image.open(io.BytesIO(content)).convert("RGB")

    try:
        text = pytesseract.image_to_string(image)
    except TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR not found. Please install it and/or set TESSERACT_CMD "
            "to the full path of tesseract.exe."
        ) from exc

    return text
