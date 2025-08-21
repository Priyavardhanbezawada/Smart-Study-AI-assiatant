import streamlit as st
import pdfplumber

def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

st.title("PDF Text Extractor")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
if uploaded_file is not None:
    pdf_text = extract_text(uploaded_file)
    st.subheader("Extracted Text")
    st.write(pdf_text if pdf_text else "No text found in PDF.")
