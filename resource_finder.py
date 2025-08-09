# resource_finder.py
import os
import sys
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nlp_helper import extract_keywords_from_topic  # Custom NLP keyword extraction

# Load environment variables from .env
load_dotenv()

# API Keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def _check_api_keys():
    """Check if required API keys are present."""
    if not all([YOUTUBE_API_KEY, GOOGLE_SEARCH_API_KEY, SEARCH_ENGINE_ID]):
        missing = []
        if not YOUTUBE_API_KEY:
            missing.append("YOUTUBE_API_KEY")
        if not GOOGLE_SEARCH_API_KEY:
            missing.append("GOOGLE_SEARCH_API_KEY")
        if not SEARCH_ENGINE_ID:
            missing.append("SEARCH_ENGINE_ID")
        print(f"Missing API keys: {', '.join(missing)}", file=sys.stderr)
        return False
    return True

def find_youtube_videos(topic: str, max_results: int = 3) -> list:
    """
    Search YouTube for tutorials related to the given topic.
    Returns a list of video titles with links.
    """
    try:
        search_query = extract_keywords_from_topic(topic)
        youtube_query = f"{search_query} tutorial explained"
        
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=youtube_query,
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
            videos.append(f"- [Video] {title}: https://www.youtube.com/watch?v={video_id}")
        return videos
    except HttpError as e:
        print(f"HTTP error {e.resp.status} while calling YouTube API: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error in find_youtube_videos: {e}", file=sys.stderr)
        return []

def find_articles(topic: str, max_results: int = 2) -> list:
    """
    Search Google Custom Search for articles related to the topic.
    """
    try:
        search_query = extract_keywords_from_topic(topic)
        article_query = f"in-depth tutorial {search_query}"

        service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
        res = service.cse().list(
            q=article_query,
            cx=SEARCH_ENGINE_ID,
            num=max_results
        ).execute()
        
        articles = []
        for item in res.get('items', []):
            title = item['title']
            link = item['link']
            articles.append(f"- [Article] {title}: {link}")
        return articles
    except HttpError as e:
        print(f"HTTP error {e.resp.status} while calling Google Search API: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error in find_articles: {e}", file=sys.stderr)
        return []

def fetch_all_resources(topic: str) -> list:
    """
    Fetch both YouTube videos and articles for the given topic.
    """
    print(f"\n🔎 Searching resources for: {topic}...")
    if not _check_api_keys():
        return ["Error: API keys are missing or invalid."]
    
    videos = find_youtube_videos(topic)
    articles = find_articles(topic)
    return videos + articles

# Debug run example
if __name__ == "__main__":
    topic_input = "Python decorators in programming"
    resources = fetch_all_resources(topic_input)
    print("\nResults:")
    for res in resources:
        print(res)
