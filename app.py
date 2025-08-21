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
st.write("Your all-in-one study assistant. Upload a syllabus to generate resources, quizzes, assignments, and a study plan.")

uploaded_file = st.file_uploader("Choose your syllabus PDF file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    if st.button("Generate Study Guide"):
        # Process PDF and get topics
        temp_file_path = os.path.join(".", uploaded_file.name)
        with open(temp_file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        with st.spinner("Analyzing syllabus..."):
            raw_text = extract_text(temp_file_path)
            topics = extract_topics(raw_text)
        os.remove(temp_file_path)

        if topics:
            st.session_state.topics = topics
            st.success(f"Successfully extracted {len(topics)} topics!")
        else:
            st.error("Could not extract topics from the PDF.")

# --- Display Topics and Features if they exist in session state ---
if 'topics' in st.session_state:
    st.header("✨ Your Personalized Study Materials ✨", divider="rainbow")

    for idx, topic in enumerate(st.session_state.topics):
        with st.expander(f"📚 {topic}"):
            # --- Resource Finder ---
            st.subheader("Recommended Resources")
            with st.spinner("Finding videos and articles..."):
                resources = find_all_resources(topic)
            
            # CORRECTED: This logic now handles cases where no resources are found.
            if not resources.get('videos') and not resources.get('articles'):
                st.write("No specific resources were found for this topic.")
            else:
                if resources.get('videos'):
                    st.write("🎥 **YouTube Videos:**")
                    for video in resources['videos']:
                        st.markdown(f"- [{video['title']}]({video['link']})")
                if resources.get('articles'):
                    st.write("📰 **Articles:**")
                    for article in resources['articles']:
                        st.markdown(f"- [{article['title']}]({article['link']})")

            st.markdown("---")

            # --- Quiz and Assignment Buttons ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧠 Generate Practice Quiz", key=f"quiz_btn_{idx}"):
                    with st.spinner("Creating quiz..."):
                        st.session_state[f'quiz_{idx}'] = generate_quiz(topic)
            with col2:
                if st.button("✍️ Generate Assignment", key=f"assign_btn_{idx}"):
                    with st.spinner("Creating assignment..."):
                        st.session_state[f'assignment_{idx}'] = generate_assignment(topic)

            # --- Display Quiz ---
            if f'quiz_{idx}' in st.session_state:
                st.subheader("Practice Quiz")
                quiz = st.session_state[f'quiz_{idx}']
                if "error" in quiz: st.error(quiz["error"])
                else:
                    for i, q in enumerate(quiz.get('questions', [])):
                        st.write(f"**Question {i+1}:** {q['question']}")
                        st.radio("Options:", q['options'], key=f"q_{idx}_{i}")

            # --- Display Assignment ---
            if f'assignment_{idx}' in st.session_state:
                st.subheader("Assignment Questions")
                assignment = st.session_state[f'assignment_{idx}']
                if "error" in assignment: st.error(assignment["error"])
                else:
                    for i, q_text in enumerate(assignment.get('assignment_questions', [])):
                        st.write(f"{i+1}. {q_text}")

    # --- Exam Schedule Planner ---
    st.header("📅 Exam Schedule Planner", divider="rainbow")
    exam_date = st.date_input("Select your exam date:", min_value=date.today())
    if st.button("Create Study Plan"):
        schedule = create_schedule(st.session_state.topics, exam_date)
        if schedule:
            st.session_state.schedule = schedule
            st.success("Study plan created!")
        else:
            st.error("Could not create schedule. Make sure the exam date is in the future.")

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

