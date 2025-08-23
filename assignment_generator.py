import os
import openai  # Groq is OpenAI compatible!
import json
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
openai.api_key = GROQ_API_KEY
openai.api_base = "https://api.groq.com/openai/v1"  # Make sure this matches Groq’s documentation

def generate_assignment(topic: str):
    if not GROQ_API_KEY:
        return {"error": "Groq API key is not configured."}
    prompt = (
        f"You are a university professor. Generate 3 short-answer assignment questions for the topic: \"{topic}\". "
        "The questions should encourage critical thinking and application of knowledge. "
        "The output must be a valid JSON object containing a single key \"assignment_questions\" which is an array of strings. "
        "Do not include any text before or after the JSON."
    )
    try:
        completion = openai.ChatCompletion.create(
            model="mixtral-8x7b-32768",  # Use your Groq model, or update as needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        response_text = completion['choices'][0]['message']['content']
        json_text = re.search(r'\{.*\}', response_text, re.DOTALL).group(0)
        return json.loads(json_text)
    except Exception as e:
        return {"error": f"Failed to generate assignment: {e}"}
