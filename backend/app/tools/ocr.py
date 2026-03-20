import os
from langchain_core.tools import tool
from typing import Optional
from app.utils.logger import setup_logger

logger = setup_logger("tools.ocr")

try:
    import pytesseract
    from PIL import Image
    import io
    import base64
    import urllib.request
except ImportError:
    logger.error("Missing imports for OCR (pytesseract, Pillow)")

@tool
def perform_image_ocr(image_source: str, source_type: str = "url") -> str:
    """
    Perform OCR (Optical Character Recognition) on an image to extract text.
    Helpful for bypassing simple image captchas or reading document screenshots during penetration testing.
    
    Args:
        image_source: The URL to the image, or absolute local file path, or base64 encoded image string.
        source_type: The type of source. Options: "url", "file", "base64"
    """
    logger.info(f"Performing OCR on {source_type} source")
    try:
        if source_type == "url":
            req = urllib.request.Request(image_source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                img_data = response.read()
            img = Image.open(io.BytesIO(img_data))
        elif source_type == "file":
            if not os.path.exists(image_source):
                return f"ERROR: File not found - {image_source}"
            img = Image.open(image_source)
        elif source_type == "base64":
            if "," in image_source: # Strip data:image/... base64 prefix
                image_source = image_source.split(",")[1]
            img_data = base64.b64decode(image_source)
            img = Image.open(io.BytesIO(img_data))
        else:
            return "ERROR: Invalid source_type. Must be 'url', 'file', or 'base64'."
            
        # Standardize for better OCR
        img = img.convert('L') # Greyscale
        text = pytesseract.image_to_string(img)
        
        logger.info("OCR successful.")
        return text.strip() if text.strip() else "NO TEXT FOUND IN IMAGE."
        
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        # Note for users on standard windows setup finding pytesseract issues
        if "tesseract is not installed" in str(e).lower() or "tesseract is not in your path" in str(e).lower():
            return "ERROR: pytesseract executable is not configured on this host machine. The system needs Tesseract-OCR binary installed."
        return f"ERROR: {str(e)}"