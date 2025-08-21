# image_parser.py
import pytesseract
from PIL import Image
import io

def extract_text_from_image(image_bytes):
    """
    Uses Tesseract OCR to extract text from an image provided as bytes.
    """
    try:
        # Open the image from the in-memory bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        
        return text
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return ""