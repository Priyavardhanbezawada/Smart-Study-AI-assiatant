import fitz  # PyMuPDF library

def extract_text(pdf_stream):
    """
    Opens a PDF from a byte stream and returns all its text content.
    A byte stream is what Flask provides when a user uploads a file.
    """
    try:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        full_text = "".join(page.get_text() for page in doc)
        return full_text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        # Return empty string on failure
        return ""
