import streamlit as st
import pdfplumber
import google.generativeai as genai
from constants import MAX_TEXT_LENGTH

genai.configure(api_key=st.secrets.gemini.api_key)

def extract_text_from_pdf(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

def get_resume_feedback(resume_text, job_field):
    prompt = f"""[SAME PROMPT TEMPLATE YOU ALREADY USE WITH f-STRINGS HERE]"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return None
