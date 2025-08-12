import streamlit as st
from pdf_parser import extract_text
from image_parser import extract_text_from_image
from topic_extractor import extract_topics
from resource_finder import fetch_all_resources
from quiz_generator import generate_quiz
from assignment_generator import generate_assignment
from schedule_planner import create_schedule, generate_calendar_file
import os
import tempfile
from datetime import date

st.set_page_config(page_title="Syllabus Genius", page_icon="🚀", layout="wide")
st.title("Syllabus Genius 🚀")
st.write("Your all-in-one study assistant. Upload a syllabus (PDF or Image) to generate resources, quizzes, and more.")

def process_file(uploaded_file):
    raw_text = ""
    suffix = uploaded_file.name.split('.')[-1].lower()
    with st.spinner("Analyzing your document... This may take a moment."):
        try:
            # Use tempfile for robustness & cleanup
            with tempfile.NamedTemporaryFile(delete=False, suffix='.'+suffix) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name

            if uploaded_file.type == "application/pdf" or suffix == "pdf":
                raw_text = extract_text(temp_file_path)
            elif uploaded_file.type.startswith("image/") or suffix in ["png", "jpg", "jpeg"]:
                with open(temp_file_path, "rb") as img_f:
                    image_bytes = img_f.read()
                raw_text = extract_text_from_image(image_bytes)
            else:
                st.error("Unsupported file type.")
                raw_text = ""
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    return raw_text

uploaded_file = st.file_uploader("Choose your syllabus file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    if st.button("Generate Study Guide"):
        raw_text = process_file(uploaded_file)
        if raw_text:
            topics = extract_topics(raw_text)
            if topics:
                st.session_state.topics = topics
                st.success(f"Successfully extracted {len(topics)} topics!")
            else:
                st.error("Could not identify any distinct topics in the document.")
        else:
            st.error("Could not read any text from the uploaded file. It might be empty or corrupted.")

if 'topics' in st.session_state:
    st.header("✨ Your Personalized Study Materials ✨", divider="rainbow")

    for idx, topic in enumerate(st.session_state.topics):
        with st.expander(f"📚 {topic}"):
            st.subheader("Recommended Resources")
            with st.spinner("Finding videos and articles..."):
                resources = fetch_all_resources(topic)
            if resources:
                for resource in resources:
                    st.markdown(resource)
            else:
                st.write("No specific resources found for this topic.")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧠 Generate Practice Quiz", key=f"quiz_btn_{idx}"):
                    with st.spinner("Creating quiz..."):
                        st.session_state[f'quiz_{idx}'] = generate_quiz(topic)
            with col2:
                if st.button("✍️ Generate Assignment", key=f"assign_btn_{idx}"):
                    with st.spinner("Creating assignment..."):
                        st.session_state[f'assignment_{idx}'] = generate_assignment(topic)
            
            # Quiz display
            if f'quiz_{idx}' in st.session_state:
                st.subheader("Practice Quiz")
                quiz = st.session_state[f'quiz_{idx}']
                if "error" in quiz:
                    st.error(quiz["error"])
                else:
                    for i, q in enumerate(quiz.get('quiz', [])):
                        st.write(f"**Question {i+1}:** {q['question']}")
                        st.radio("Options:", q['options'], key=f"q_{idx}_{i}")

            # Assignment display
            if f'assignment_{idx}' in st.session_state:
                st.subheader("Assignment Questions")
                assignment = st.session_state[f'assignment_{idx}']
                if "error" in assignment:
                    st.error(assignment["error"])
                else:
                    for i, q_text in enumerate(assignment.get('assignment_questions', [])):
                        st.write(f"{i+1}. {q_text}")

    st.header("📅 Exam Schedule Planner", divider="rainbow")
    exam_date = st.date_input("Select your exam date:", min_value=date.today())
    if st.button("Create Study Plan"):
        schedule = create_schedule(st.session_state.topics, exam_date)
        if schedule:
            st.session_state.schedule = schedule
            st.success("Study plan created!")
        else:
            st.error("Could not create schedule.")

    if 'schedule' in st.session_state:
        st.subheader("Your Study Plan")
        for day, daily_topics in st.session_state.schedule.items():
            st.markdown(f"**{day}**: Study `{', '.join(daily_topics)}`")
        calendar_data = generate_calendar_file(st.session_state.schedule)
        st.download_button(
            label="📅 Download Calendar File (.ics)",
            data=calendar_data,
            file_name="study_schedule.ics",
            mime="text/calendar"
        )
