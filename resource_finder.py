import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- API Keys and IDs from Environment Variables ---
# Securely load your keys. These MUST be in your .env file.
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
Google Search_API_KEY = os.getenv("Google Search_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID") # Important: You need this for the article search

def find_youtube_videos(query: str, max_results: int = 5):
    """
    Finds YouTube videos for a given query using the YouTube Data API v3.
    """
    if not YOUTUBE_API_KEY:
        print("🔴 ERROR: YOUTUBE_API_KEY is not set in the environment variables.")
        return []

    # API endpoint and parameters
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'type': 'video',
        'maxResults': max_results
    }

    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=10) # 10-second timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        data = response.json()
        videos = []
        for item in data.get('items', []):
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            video_link = f"https://www.youtube.com/watch?v={video_id}"
            videos.append({'title': video_title, 'link': video_link})
        
        print(f"✅ Found {len(videos)} YouTube videos for '{query}'.")
        return videos

    except requests.exceptions.HTTPError as http_err:
        print(f"🔴 HTTP Error while fetching YouTube videos: {http_err}")
        print(f"   Response Body: {response.text}") # This will show the exact error from Google
    except requests.exceptions.RequestException as err:
        print(f"🔴 A network error occurred while fetching YouTube videos: {err}")
    except Exception as e:
        print(f"🔴 An unexpected error occurred in find_youtube_videos: {e}")
    
    return [] # Return empty list if any error occurs

def find_articles(query: str, max_results: int = 5):
    """
    Finds articles and web pages for a given query using the Google Custom Search JSON API.
    """
    if not Google Search_API_KEY or not SEARCH_ENGINE_ID:
        print("🔴 ERROR: Google Search_API_KEY or SEARCH_ENGINE_ID is not set.")
        return []

    # API endpoint and parameters
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': Google Search_API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'num': max_results
    }

    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=10) # 10-second timeout
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()
        articles = []
        for item in data.get('items', []):
            article_title = item.get('title')
            article_link = item.get('link')
            article_snippet = item.get('snippet')
            articles.append({'title': article_title, 'link': article_link, 'snippet': article_snippet})
        
        print(f"✅ Found {len(articles)} articles for '{query}'.")
        return articles

    except requests.exceptions.HTTPError as http_err:
        print(f"🔴 HTTP Error while fetching articles: {http_err}")
        print(f"   Response Body: {response.text}") # This will show the exact error from Google
    except requests.exceptions.RequestException as err:
        print(f"🔴 A network error occurred while fetching articles: {err}")
    except Exception as e:
        print(f"🔴 An unexpected error occurred in find_articles: {e}")

    return [] # Return empty list if any error occurs

def find_all_resources(topic: str):
    """
    A main function to find all resources (videos and articles) for a given topic.
    This is the function your app.py should call.
    """
    print(f"\n🔎 Finding resources for topic: '{topic}'")
    videos = find_youtube_videos(topic)
    articles = find_articles(topic)
    
    return {
        'videos': videos,
        'articles': articles
    }

# --- This part is for testing the script directly ---
if __name__ == '__main__':
    # You can run "python resource_finder.py" in your terminal to test this.
    test_topic = "Software Development Life Cycle"
    resources = find_all_resources(test_topic)
    
    print("\n--- TEST RESULTS ---")
    print(f"\n🎥 YouTube Videos Found: {len(resources['videos'])}")
    for video in resources['videos']:
        print(f"  - {video['title']}: {video['link']}")
        
    print(f"\n📰 Articles Found: {len(resources['articles'])}")
    for article in resources['articles']:
        print(f"  - {article['title']}: {article['link']}")
    print("\n--- END OF TEST ---")
