# assignment_generator.py
import os
import google.generativeai as genai
import json
import re

try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

def generate_assignment(topic: str):
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key is not configured."}
        
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"""
    You are a university professor. Generate 3 short-answer assignment questions for the topic: "{topic}".
    The questions should encourage critical thinking and application of knowledge.
    The output must be a valid JSON object containing a single key "assignment_questions" which is an array of strings.
    Do not include any text before or after the JSON.
    """

    try:
        response = model.generate_content(prompt)
        json_text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        return json.loads(json_text)
    except Exception as e:
        return {"error": f"Failed to generate assignment: {e}"}