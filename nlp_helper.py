# nlp_helper.py
import os
import re
import time
import google.generativeai as genai

# ======================
# API Configuration
# ======================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY environment variable is not set.")

genai.configure(api_key=GEMINI_API_KEY)


# ======================
# Keyword Extraction
# ======================
def extract_keywords_from_topic(topic_sentence: str, retries: int = 2, delay: float = 1.5) -> str:
    """
    Extracts the 2–4 most important keywords from a syllabus topic sentence
    using Google Gemini AI.
    
    Args:
        topic_sentence (str): The input sentence from which to extract keywords.
        retries (int): Number of retry attempts if extraction fails.
        delay (float): Delay between retries in seconds.
    
    Returns:
        str: Extracted keywords separated by spaces. Falls back to original sentence on failure.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Extract the core 2–4 keywords from the following syllabus sentence.
    Only return the keywords separated by spaces — no numbering, punctuation, or extra text.
    Do not add explanations.

    Sentence: "{topic_sentence}"
    """

    last_error = None

    for attempt in range(retries + 1):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "text/plain"}  # Force plain text
            )
            keywords = response.text.strip()

            # Clean unwanted punctuation/symbols
            keywords = re.sub(r"[^a-zA-Z0-9\s]", "", keywords)

            # Ensure word count is reasonable
            words = keywords.split()
            if 2 <= len(words) <= 6:
                return keywords.lower()  # Lowercase for search friendliness
            else:
                last_error = f"Unexpected keyword count ({len(words)})"
        
        except Exception as e:
            last_error = f"Gemini request failed: {e}"

        # Retry if needed
        if attempt < retries:
            time.sleep(delay)

    # Fallback: return original sentence if all attempts fail
    print(f"⚠️ Keyword extraction failed: {last_error}")
    return topic_sentence


# ======================
# CLI for Testing
# ======================
if __name__ == "__main__":
    sentence = input("Enter a syllabus sentence: ").strip()
    print("Extracted Keywords:", extract_keywords_from_topic(sentence))
