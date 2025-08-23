import os
import openai  # Groq's API is OpenAI-compatible
import json
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")  # Default Groq API endpoint

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")

openai.api_key = GROQ_API_KEY
openai.api_base = GROQ_API_BASE

def generate_quiz(topic: str):
    prompt = f"""
You are an expert quiz creator. Generate a 3-question multiple-choice quiz on the topic: "{topic}".
The output must be a valid JSON object. Do not include any text before or after the JSON.
Each question should have a "question" field, an "options" field (an array of 4 strings), and an "answer" field (the correct option string).
"""
    try:
        response = openai.ChatCompletion.create(
            model="llama3-8b-8192",  # Or another recommended Groq model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.7
        )
        content = response["choices"]["message"]["content"]
        json_text = re.search(r'{.*}', content, re.DOTALL).group(0)
        return json.loads(json_text)
    except Exception as e:
        return {"error": f"Failed to generate quiz: {e}"}
