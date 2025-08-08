# resource_finder.py
import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def _check_api_keys():
    """Check if all required API keys are configured."""
    if not all([YOUTUBE_API_KEY, GOOGLE_SEARCH_API_KEY, SEARCH_ENGINE_ID]):
        print("Error: Missing API keys in .env file or environment. Please check your configuration.", file=sys.stderr)
        return False
    return True

def find_youtube_videos(topic: str, max_results: int = 3) -> list:
    """Search YouTube for videos about a given topic."""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        search_query = f"{topic} tutorial explained"
        request = youtube.search().list(
            q=search_query,
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en'
        )
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
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []

def find_articles(topic: str, max_results: int = 2) -> list:
    """Use Google Custom Search to find articles about a given topic."""
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        search_query = f"in-depth tutorial {topic}"
        res = service.cse().list(q=search_query, cx=SEARCH_ENGINE_ID, num=max_results).execute()
        articles = []
        for item in res.get('items', []):
            title = item['title']
            link = item['link']
            articles.append(f"  - [Article] {title}: {link}")
        return articles
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred while calling Google Search API.", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []

def fetch_all_resources(topic: str) -> list:
    """Fetch both YouTube videos and articles about the topic."""
    print(f"\n🔎 Searching resources for: {topic}...")
    if not _check_api_keys():
        return ["Error: API keys are not configured correctly."]
    videos = find_youtube_videos(topic)
    articles = find_articles(topic)
    return videos + articles

# Optional: test code
if __name__ == "__main__":
    topic = "Python programming"
    resources = fetch_all_resources(topic)
    for r in resources:
        print(r)
