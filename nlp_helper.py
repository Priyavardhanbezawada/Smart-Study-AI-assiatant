# nlp_helper.py
import os
import re
import time
import groq

# ======================
# API Configuration
# ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("❌ GROQ_API_KEY environment variable is not set.")

client = groq.Groq(api_key=GROQ_API_KEY)


# ======================
# Keyword Extraction
# ======================
def extract_keywords_from_topic(topic_sentence: str, retries: int = 2, delay: float = 1.5) -> str:
    """
    Extracts the 2–4 most important keywords from a syllabus topic sentence
    using Groq.
    """
    prompt = f"""
    Extract the core 2–4 keywords from the following syllabus sentence.
    Only return the keywords separated by spaces — no numbering, punctuation, or extra text.
    Do not add explanations.

    Sentence: "{topic_sentence}"
    """

    last_error = None

    for attempt in range(retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                # Using a faster model to prevent timeouts
                model="llama3-8b-8192",
                temperature=0.2,
            )
            keywords = chat_completion.choices[0].message.content.strip()
            keywords = re.sub(r"[^a-zA-Z0-9\s]", "", keywords)
            words = keywords.split()
            
            if 2 <= len(words) <= 6:
                return keywords.lower()
            else:
                last_error = f"Unexpected keyword count ({len(words)})"
        
        except Exception as e:
            last_error = f"Groq request failed: {e}"

        if attempt < retries:
            time.sleep(delay)

    print(f"⚠️ Keyword extraction failed: {last_error}")
    return topic_sentence


# ======================
# CLI for Testing
# ======================
if __name__ == "__main__":
    sentence = input("Enter a syllabus sentence: ").strip()
    print("Extracted Keywords:", extract_keywords_from_topic(sentence))
