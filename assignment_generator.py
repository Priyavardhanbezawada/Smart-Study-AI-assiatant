# assignment_generator.py
import os
import google.generativeai as genai
import json
import re
import time

# =======================
# API Config
# =======================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("❌ GEMINI_API_KEY is not set. Please set it before running.")

genai.configure(api_key=GEMINI_API_KEY)


# =======================
# Assignment Generator
# =======================
def generate_assignment(topic: str, num_questions: int = 3, retries: int = 2, delay: float = 1.5) -> dict:
    """
    Generates short-answer assignment questions for the given topic.
    
    Args:
        topic (str): The assignment topic.
        num_questions (int): Number of questions to generate.
        retries (int): Retry attempts if JSON parsing fails.
        delay (float): Delay in seconds between retries.
    
    Returns:
        dict: {"assignment_questions": [...]} or {"error": "..."}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are a university professor.
    Generate {num_questions} short-answer assignment questions for the topic: "{topic}".
    The questions should encourage critical thinking and application of knowledge.
    The output must be **strict valid JSON** in the format:
    {{
      "assignment_questions": [
        "Question 1 text",
        "Question 2 text",
        ...
      ]
    }}
    Rules:
    - No extra text, explanations, or formatting outside JSON.
    - Do not number the questions in text; just provide them as strings in the array.
    """

    for attempt in range(retries + 1):
        try:
            # Ask Gemini for JSON
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # Try direct JSON parse
            return json.loads(response.text)

        except json.JSONDecodeError:
            # Try to extract JSON if mixed with text
            cleaned_text = _extract_json_from_text(response.text)
            if cleaned_text:
                try:
                    return json.loads(cleaned_text)
                except json.JSONDecodeError as je:
                    last_error = f"JSON parse error after cleaning: {je}"
            else:
                last_error = "Could not find JSON in Gemini response."

        except Exception as e:
            last_error = f"Gemini API request failed: {e}"

        # Retry if needed
        if attempt < retries:
            time.sleep(delay)

    return {
        "error": f"Failed to generate assignment after {retries+1} attempts. {last_error}",
        "raw_response": response.text if "response" in locals() else None
    }


# =======================
# Helper: Extract JSON from text
# =======================
def _extract_json_from_text(text: str) -> str:
    """Extracts JSON object from string using regex."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0).strip() if match else None


# =======================
# CLI Test
# =======================
if __name__ == "__main__":
    topic_input = input("Enter assignment topic: ").strip()
    num_qs_input = input("Number of questions (default 3): ").strip()
    num_qs = int(num_qs_input) if num_qs_input.isdigit() else 3

    assignment_data = generate_assignment(topic_input, num_questions=num_qs)
    print(json.dumps(assignment_data, indent=2, ensure_ascii=False))
