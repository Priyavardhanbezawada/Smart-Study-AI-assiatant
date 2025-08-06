# pdf_parser.py
import fitz  # PyMuPDF
import sys

def extract_text(pdf_path: str) -> str:
    """Extracts raw text content from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        if not text.strip():
            print(f"Warning: No text could be extracted from {pdf_path}. The PDF might be image-based.")
        return text
    except Exception as e:
        print(f"Error opening or reading PDF file: {e}", file=sys.stderr)
        return ""