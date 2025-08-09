# nlp_helper.py
import os
import google.generativeai as genai

# Configure the API key from environment variables
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API for NLP helper: {e}")

def extract_keywords_from_topic(topic_sentence: str) -> str:
    """
    Uses the Gemini AI to extract the most important keywords from a long topic sentence.
    """
    if not GEMINI_API_KEY:
        return topic_sentence # Return the original topic if the key isn't configured

    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        prompt = f"""
        Analyze the following sentence from a university syllabus and extract the core 2-4 keywords that would be best for finding tutorial videos on Google and YouTube. Return only the keywords, separated by a space.

        Sentence: "{topic_sentence}"
        
        Example:
        Sentence: "For many types of software, design and construction are interleaved"
        Keywords: software design interleaved construction
        
        Keywords:
        """

        response = model.generate_content(prompt)
        # Clean up the response to get just the keywords
        keywords = response.text.strip()
        
        # If the AI returns something strange, fall back to the original topic
        if len(keywords) > len(topic_sentence) or len(keywords) == 0:
            return topic_sentence

        return keywords

    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        # If AI fails, just use the original topic sentence
        return topic_sentence
