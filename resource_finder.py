# resource_finder.py
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# Load environment variables from the .env file
load_dotenv()

def find_youtube_videos(query: str, max_results: int = 5):
    """
    Finds YouTube videos for a given query using DuckDuckGo Search.
    No API key needed.
    """
    videos = []
    print(f"✅ Searching for YouTube videos on: '{query}'")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.videos(
                f"{query} site:youtube.com",
                safesearch='on',
                resolution='high',
                max_results=max_results
            ))

        for item in results:
            videos.append({
                'title': item.get('title'),
                'link': item.get('content')
            })
        return videos
        
    except Exception as e:
        print(f"🔴 An unexpected error occurred in find_youtube_videos: {e}")
    
    return []

def find_articles(query: str, max_results: int = 5):
    """
    Finds articles and web pages using DuckDuckGo search. No API key needed.
    """
    articles = []
    print(f"✅ Searching for articles on: '{query}'")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        for item in results:
            articles.append({
                'title': item.get('title'),
                'link': item.get('href'),
                'snippet': item.get('body')
            })
        return articles
    except Exception as e:
        print(f"🔴 An unexpected error occurred in find_articles: {e}")
    
    return []

def find_all_resources(topic: str):
    """
    A main function to find all resources (videos and articles) for a given topic.
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
    test_topic = "Software Development Life Cycle"
    resources = find_all_resources(test_topic)
    
    print("\n--- TEST RESULTS ---")
    if resources['videos']:
        print(f"\n🎥 YouTube Videos Found: {len(resources['videos'])}")
        for video in resources['videos']:
            print(f"  - {video['title']}: {video['link']}")
    
    if resources['articles']:
        print(f"\n📰 Articles Found: {len(resources['articles'])}")
        for article in resources['articles']:
            print(f"  - {article['title']}: {article['link']}")
    print("\n--- END OF TEST ---")
