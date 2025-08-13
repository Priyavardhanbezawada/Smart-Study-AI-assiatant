# resource_finder.py
import os
import re
import groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# =======================
# API Config
# =======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("❌ GROQ_API_KEY is not set. Please set it before running.")

client = groq.Groq(api_key=GROQ_API_KEY)


def _perform_web_search(prompt: str, max_results: int) -> list:
    """
    Asks the Groq model to perform a web search and returns parsed results.
    """
    full_prompt = f"""
    You have access to a web search tool.
    Please perform a web search to find the top {max_results} results for the following query.
    Return the results as a markdown list with each item in the format: [Title](URL)

    Query: "{prompt}"
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="openai/gpt-oss-120b",
            # Enable the web search tool
            tools=[{"type": "web_search"}],
            temperature=0.2,
        )
        response_text = chat_completion.choices[0].message.content

        # Parse the markdown links from the response
        # Regex to find all occurrences of [Title](URL)
        matches = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", response_text)
        
        results = [{'title': title, 'link': link} for title, link in matches]
        return results[:max_results]

    except Exception as e:
        print(f"🔴 An error occurred during web search: {e}")
        return []

def find_youtube_videos(query: str, max_results: int = 5):
    """
    Finds YouTube videos using the model's web search tool.
    """
    print(f"✅ Searching for YouTube videos on: '{query}'")
    # Frame the query to be specific to YouTube
    search_prompt = f"Top {max_results} YouTube videos about '{query}'"
    return _perform_web_search(search_prompt, max_results)


def find_articles(query: str, max_results: int = 5):
    """
    Finds articles and web pages using the model's web search tool.
    """
    print(f"✅ Searching for articles on: '{query}'")
    # Frame the query for general educational articles
    search_prompt = f"Top {max_results} educational articles or tutorials about '{query}'"
    return _perform_web_search(search_prompt, max_results)


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
