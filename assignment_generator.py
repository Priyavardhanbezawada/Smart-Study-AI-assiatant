# assignment_generator.py
import os
import groq
import json
import re
import time

# =======================
# API Config
# =======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("❌ GROQ_API_KEY is not set. Please set it before running.")

client = groq.Groq(api_key=GROQ_API_KEY)


# =======================
# Assignment Generator
# =======================
def generate_assignment(topic: str, num_questions: int = 3, retries: int = 2, delay: float = 1.5) -> dict:
    """
    Generates short-answer assignment questions for the given topic using Groq.
    
    Args:
        topic (str): The assignment topic.
        num_questions (int): Number of questions to generate.
        retries (int): Retry attempts if JSON parsing fails.
        delay (float): Delay in seconds between retries.
    
    Returns:
        dict: {"assignment_questions": [...]} or {"error": "..."}
    """

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
            # Ask Groq for JSON
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_text = chat_completion.choices[0].message.content

            # Try direct JSON parse
            return json.loads(response_text)

        except json.JSONDecodeError:
            # Try to extract JSON if mixed with text
            cleaned_text = _extract_json_from_text(response_text)
            if cleaned_text:
                try:
                    return json.loads(cleaned_text)
                except json.JSONDecodeError as je:
                    last_error = f"JSON parse error after cleaning: {je}"
            else:
                last_error = "Could not find JSON in Groq response."

        except Exception as e:
            last_error = f"Groq API request failed: {e}"

        # Retry if needed
        if attempt < retries:
            time.sleep(delay)

    return {
        "error": f"Failed to generate assignment after {retries+1} attempts. {last_error}",
        "raw_response": response_text if "response_text" in locals() else None
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
