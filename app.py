# app.py
import streamlit as st
import tempfile
from pdf_parser import extract_text
from topic_extractor import extract_topics
from resource_finder import fetch_all_resources
from quiz_generator import generate_quiz
from assignment_generator import generate_assignment
from schedule_planner import create_schedule, generate_calendar_file
from datetime import date

# -----------------------
# Streamlit Page Settings
# -----------------------
st.set_page_config(page_title="Syllabus Genius", page_icon="🚀", layout="wide")

st.title("Syllabus Genius 🚀")
st.write("Your all-in-one AI-powered study assistant. Upload your syllabus and get resources, quizzes, assignments, and a complete study plan.")

# ----------------------------------
# File Upload & Topic Extraction
# ----------------------------------
uploaded_file = st.file_uploader("📄 Upload your syllabus PDF", type="pdf")

if uploaded_file is not None:
    if st.button("🔍 Analyze Syllabus"):
        with st.spinner("Extracting topics from syllabus..."):
            # Use a temporary file to avoid filename conflicts
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name

            try:
                raw_text = extract_text(tmp_path)
                topics = extract_topics(raw_text)
            finally:
                # Ensure temp file is deleted
                import os
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if topics:
            st.session_state.topics = topics
            st.success(f"✅ Found {len(topics)} topics in your syllabus!")
        else:
            st.error("❌ Could not extract any topics from the provided PDF.")

# ----------------------------------
# If topics are loaded, show features
# ----------------------------------
if "topics" in st.session_state:
    st.header("✨ Your Personalized Study Materials ✨", divider="rainbow")

    for idx, topic in enumerate(st.session_state.topics):
        
        with st.expander(f"📚 {topic}"):
            # --- 1. Recommended Resources ---
            st.subheader("📌 Recommended Resources")
            with st.spinner("Searching videos and articles..."):
                resources = fetch_all_resources(topic)
            if resources:
                for res in resources:
                    st.markdown(res)
            else:
                st.warning("No resources found for this topic.")

            st.markdown("---")

            # --- 2. Quiz & Assignment Buttons ---
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧠 Practice Quiz", key=f"quiz_btn_{idx}"):
                    with st.spinner("Creating your quiz..."):
                        quiz_result = generate_quiz(topic)
                    st.session_state[f'quiz_{idx}'] = quiz_result

            with col2:
                if st.button("✍️ Assignment", key=f"assign_btn_{idx}"):
                    with st.spinner("Creating your assignment..."):
                        assign_result = generate_assignment(topic)
                    st.session_state[f'assignment_{idx}'] = assign_result

            # --- 3. Display Quiz ---
            if f'quiz_{idx}' in st.session_state:
                st.subheader("🧠 Practice Quiz")
                quiz_data = st.session_state[f'quiz_{idx}']
                if "error" in quiz_data:
                    st.error(quiz_data['error'])
                else:
                    # Expecting format: {"questions": [ { "question": ..., "options": [...], "answer": ... } ]}
                    for q_num, q in enumerate(quiz_data.get("questions", []), start=1):
                        st.write(f"**Question {q_num}:** {q['question']}")
                        st.radio("Options:", q['options'], key=f"quiz_{idx}_q{q_num}")

            # --- 4. Display Assignment ---
            if f'assignment_{idx}' in st.session_state:
                st.subheader("✍️ Assignment Questions")
                assign_data = st.session_state[f'assignment_{idx}']
                if "error" in assign_data:
                    st.error(assign_data['error'])
                else:
                    for a_num, a_text in enumerate(assign_data.get("assignment_questions", []), start=1):
                        st.write(f"{a_num}. {a_text}")

    # ----------------------------------
    # Exam Schedule Planner
    # ----------------------------------
    st.header("📅 Exam Schedule Planner", divider="rainbow")
    exam_date = st.date_input("Select your exam date:", min_value=date.today())
    
    if st.button("📆 Create Study Plan"):
        with st.spinner("Generating study plan..."):
            schedule = create_schedule(st.session_state.topics, exam_date)
        if schedule:
            st.session_state.schedule = schedule
            st.success("✅ Study plan created successfully!")
        else:
            st.error("❌ Failed to create schedule. Select a future date.")

    # Show schedule if available
    if 'schedule' in st.session_state:
        st.subheader("📋 Your Study Plan")
        for day, daily_topics in st.session_state.schedule.items():
            st.markdown(f"**{day}**: {', '.join(daily_topics)}")
        
        # Calendar download
        calendar_data = generate_calendar_file(st.session_state.schedule)
        st.download_button(
            label="💾 Download Calendar (.ics)",
            data=calendar_data,
            file_name="study_schedule.ics",
            mime="text/calendar"
        )
