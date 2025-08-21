import os
import spacy
from flask import Flask, request, render_template, redirect, url_for
from googleapiclient.discovery import build
from pdf_parser import extract_text  # Custom module to extract PDF text

# --- CONFIGURATION & SETUP ---

app = Flask(__name__)
API_KEY = os.environ.get("YOUTUBE_API_KEY")

# Load NLP model and connect to the YouTube API
print("Loading NLP model...")
nlp = spacy.load("en_core_web_sm")
print("Connecting to YouTube API...")
youtube_service = build('youtube', 'v3', developerKey=API_KEY)

# --- HELPER FUNCTION ---
def find_youtube_tutorial(topic):
    """Searches YouTube for a topic and returns the top result's link."""
    try:
        query = f"{topic} tutorial explained"
        search_request = youtube_service.search().list(
            q=query, part='snippet', maxResults=1, type='video'
        )
        response = search_request.execute()
        if response.get('items'):
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
        return "No video found."
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return "Error searching for video."

# --- WEB ROUTES ---

@app.route('/')
def index():
    """Renders the main upload page (index.html)."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_syllabus():
    """Handles the file upload and processes the syllabus."""
    if 'syllabus_file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['syllabus_file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return "Error: Please upload a valid PDF file."
    # 1. Extract text
    raw_text = extract_text(file.stream.read())
    # 2. Identify topics using spaCy
    doc = nlp(raw_text)
    topics = {
        chunk.text.strip()
        for chunk in doc.noun_chunks
        if len(chunk.text.split()) > 1 and len(chunk.text) > 5
    }
    # 3. Find a YouTube video for each topic
    results = {topic: find_youtube_tutorial(topic) for topic in sorted(list(topics))}
    # 4. Render the results page
    return render_template('results.html', results=results)
