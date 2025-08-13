# quiz_generator.py
import os
import groq
import json
import re
import time


# ========================
# Groq API Configuration
# ========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "❌ Environment variable GROQ_API_KEY is not set. Please set it before running this script."
    )

client = groq.Groq(api_key=GROQ_API_KEY)


# ========================
# Quiz Generation Function
# ========================
def generate_quiz(topic: str, num_questions: int = 3, retries: int = 2, delay: float = 1.5) -> dict:
    """
    Generates a multiple-choice quiz on the given topic using Groq.
    """
    prompt = f"""
    You are an expert quiz creator.
    Generate a {num_questions}-question multiple-choice quiz on the topic: "{topic}".
    The output MUST be a strict JSON object in this exact format:
    {{
      "questions": [
        {{
          "question": "string",
          "options": ["string", "string", "string", "string"],
          "answer": "exact correct option string"
        }},
        ...
      ]
    }}
    Rules:
    - No explanations or additional text.
    - Escape special characters properly.
    - Ensure the JSON is valid.
    """

    for attempt in range(retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_text = chat_completion.choices[0].message.content
            return json.loads(response_text)

        except json.JSONDecodeError:
            cleaned_text = _extract_json_from_text(response_text)
            if cleaned_text:
                try:
                    return json.loads(cleaned_text)
                except json.JSONDecodeError as je:
                    last_error = f"JSON parse error after cleaning: {je}"
            else:
                last_error = "Could not find JSON in response."

        except Exception as e:
            last_error = f"Request failed: {e}"

        if attempt < retries:
            time.sleep(delay)

    return {
        "error": f"Failed to generate quiz after {retries+1} attempts. {last_error}",
        "raw_response": response_text if "response_text" in locals() else None
    }


# ========================
# Helper: Extract JSON
# ========================
def _extract_json_from_text(text: str) -> str:
    """Extracts JSON object from text using regex."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0).strip() if match else None


# ========================
# Save Quiz to File
# ========================
def save_quiz_to_file(quiz_data: dict, filename: str):
    """Saves quiz dictionary to a formatted JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Quiz saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save quiz: {e}")


# ========================
# Main Execution
# ========================
if __name__ == "__main__":
    topic_input = input("Enter quiz topic: ").strip()
    num_qs = input("Enter number of questions (default 3): ").strip()
    num_qs = int(num_qs) if num_qs.isdigit() else 3

    quiz_data = generate_quiz(topic_input, num_questions=num_qs)
    print(json.dumps(quiz_data, indent=2, ensure_ascii=False))

    save_choice = input("Save quiz to file? (y/n): ").strip().lower()
    if save_choice == "y":
        filename = f"quiz_{topic_input.replace(' ', '_')}.json"
        save_quiz_to_file(quiz_data, filename)
