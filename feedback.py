# app/feedback.py
import google.generativeai as genai
from .prompts import get_resume_feedback_prompt

def get_resume_feedback(resume_text, job_field, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = get_resume_feedback_prompt(resume_text, job_field)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"
