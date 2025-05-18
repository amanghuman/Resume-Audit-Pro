import streamlit as st
from app.pdf_utils import extract_text_from_pdf
from app.feedback import get_resume_feedback

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 Resume Analyzer")

api_key = st.text_input("🔑 Enter your Gemini API Key", type="password")
job_field = st.text_input("💼 Target Job Field (e.g., Data Scientist)")
uploaded_file = st.file_uploader("📎 Upload your resume (PDF only)", type=["pdf"])

if uploaded_file and api_key and job_field:
    with st.spinner("Extracting text from PDF..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text:
        with st.spinner("Generating feedback..."):
            feedback = get_resume_feedback(resume_text, job_field, api_key)
        st.markdown("## 📝 Feedback")
        st.markdown(feedback)
    else:
        st.error("❌ Could not extract text from the PDF.")
