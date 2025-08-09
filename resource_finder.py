# resource_finder.py
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
from nlp_helper import extract_keywords_from_topic # <-- Import the new function

load_dotenv()

# ... (The first part with your API key variables remains the same) ...
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
Google Search_API_KEY = os.getenv("Google Search_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def _check_api_keys():
    if not all([YOUTUBE_API_KEY, Google Search_API_KEY, SEARCH_ENGINE_ID]):
        return False
    return True

def find_youtube_videos(topic: str, max_results: int = 3) -> list:
    try:
        # --- NEW: Get keywords before searching ---
        search_query = extract_keywords_from_topic(topic)
        youtube_query = f"{search_query} tutorial explained"

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = Youtube().list(
            q=youtube_query, # <-- Use the improved query
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en'
        )
        # ... (The rest of this function remains the same) ...
        response = request.execute()
        videos = []
        for item in response.get('items', []):
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            videos.append(f"  - [Video] {title}: https://www.youtube.com/watch?v={video_id}")
        return videos
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred while calling YouTube API.", file=sys.stderr)
        return []

def find_articles(topic: str, max_results: int = 2) -> list:
    try:
        # --- NEW: Get keywords before searching ---
        search_query = extract_keywords_from_topic(topic)
        article_query = f"in-depth tutorial {search_query}"

        service = build("customsearch", "v1", developerKey=Google Search_API_KEY)
        res = service.cse().list(
            q=article_query, # <-- Use the improved query
            cx=SEARCH_ENGINE_ID, 
            num=max_results
        ).execute()
        # ... (The rest of this function remains the same) ...
        articles = []
        for item in res.get('items', []):
            title = item['title']
            link = item['link']
            articles.append(f"  - [Article] {title}: {link}")
        return articles
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred while calling Google Search API.", file=sys.stderr)
        return []

def fetch_all_resources(topic: str) -> list:
    print(f"\n🔎 Searching resources for: {topic}...")
    if not _check_api_keys():
        return ["Error: API keys are not configured correctly."]
    
    videos = find_youtube_videos(topic)
    articles = find_articles(topic)
    return videos + articles
