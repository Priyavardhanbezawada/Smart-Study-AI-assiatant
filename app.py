# File: app.py
import streamlit as st
import os
from pathlib import Path

# --- IMPORTANT: We are now importing from your new package! ---
# Make sure the function names here match the ones in your files.
from src.syllabus_helper.parser import parse_pdf_text
from src.syllabus_helper.extractor import extract_topics 
from src.syllabus_helper.curator import find_and_rank_resources 

# --- Web Page Setup ---
st.set_page_config(layout="wide")
st.title("📚 Smart Study Resource Generator")
st.write("Upload your course syllabus (PDF) and get a list of supplementary learning resources.")

# --- File Uploader Widget ---
uploaded_file = st.file_uploader("Choose a syllabus PDF", type="pdf")

# --- Main Logic: Runs only when a file is uploaded ---
if uploaded_file is not None:
    # We must save the uploaded file to read it
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / uploaded_file.name

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Show a "spinner" while the work is being done
    with st.spinner('Analyzing your syllabus... this can take a moment.'):

        # 1. Parse the PDF to get text
        document_text = parse_pdf_text(str(temp_file_path))

        # 2. Extract topics from the text
        topics = extract_topics(document_text)

        if not topics:
            st.error("Could not find any topics in the syllabus. The PDF might be image-based or have an unusual format.")
        else:
            st.success(f"Found {len(topics)} topics! Now finding resources...")

            # 3. For each topic, find and display resources
            for topic in topics:
                st.subheader(f"Resources for: {topic}")
                # You can change the limit to find more/fewer resources
                resources = find_and_rank_resources(topic, limit=3) 

                if not resources:
                    st.write("_No online resources found for this topic._")
                else:
                    for res in resources:
                        # This part assumes your resource finder returns a dictionary with 'title' and 'url'
                        st.markdown(f"▶️ **[{res.get('title', 'No Title')}]({res.get('url', '#')})**")

    # Clean up by deleting the temporary file
    os.remove(temp_file_path)
