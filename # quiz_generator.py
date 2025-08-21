# quiz_generator.py
import os
import google.generativeai as genai
import json
import re

try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

def generate_quiz(topic: str):
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key is not configured."}

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"""
    You are an expert quiz creator. Generate a 3-question multiple-choice quiz on the topic: "{topic}".
    The output must be a valid JSON object. Do not include any text before or after the JSON.
    Each question should have a "question" field, an "options" field (an array of 4 strings), and an "answer" field (the correct option string).
    """

    try:
        response = model.generate_content(prompt)
        json_text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        return json.loads(json_text)
    except Exception as e:
        return {"error": f"Failed to generate quiz: {e}"}