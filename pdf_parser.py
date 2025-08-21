import streamlit as st
import pdfplumber

def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

st.title("PDF Text Extractor")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")
if uploaded_file is not None:
    text = extract_text(uploaded_file)
    st.subheader("Extracted Text")
    st.write(text if text else "No text found in the PDF.")
