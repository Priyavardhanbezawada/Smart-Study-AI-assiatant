# app.py
import streamlit as st
from pdf_parser import extract_text
from topic_extractor import extract_topics
from resource_finder import find_all_resources
from quiz_generator import generate_quiz
from assignment_generator import generate_assignment
from schedule_planner import create_schedule, generate_calendar_file
import time
import os
from datetime import date

st.set_page_config(page_title="Syllabus Genius", page_icon="🚀", layout="wide")

# --- Main App Interface ---
st.title("Syllabus Genius 🚀")
st.write(
    "Your all-in-one study assistant. Upload a syllabus to generate resources, quizzes, assignments, and a study plan."
)

uploaded_file = st.file_uploader(
    "Choose your syllabus PDF file",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    if st.button("Generate Study Guide"):
        # Process PDF and get topics
        temp_file_path = os.path.join(".", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Analyzing syllabus..."):
            raw_text = extract_text(temp_file_path)
            topics = extract_topics(raw_text)
        os.remove(temp_file_path)
        if topics:
            st.session_state.topics = topics
            st.success(f"Successfully extracted {len(topics)} topics!")
        else:
            st.error("Could not extract topics from the PDF.")
