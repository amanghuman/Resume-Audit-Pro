import streamlit as st
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
import os
from streamlit_lottie import st_lottie
import requests

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(
    page_title="Resume Audit Pro",
    page_icon="",
    layout="wide"
)

# Apply custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_resume = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

# Header
st.markdown("<h1 class='title'>Resume Audit Pro</h1>", unsafe_allow_html=True)
st_lottie(lottie_resume, height=180, key="audit-animation")

# File upload
st.markdown("## Upload Resume")
pdf_file = st.file_uploader("Upload your resume as a PDF", type=["pdf"])

# Job description input
st.markdown("## Job Description")
job_description = st.text_area("Paste the job description", height=220)

# Run audit
if st.button("Run Resume Audit"):
    if not pdf_file or not job_description:
        st.error("Please upload a resume and paste a job description.")
    else:
        with pdfplumber.open(pdf_file) as pdf:
            resume_text = "".join([page.extract_text() or "" for page in pdf.pages])

        prompt = f"""
        You are an expert resume auditor. Review the resume below against the job description.
        Provide detailed, actionable feedback on formatting, keyword alignment, skills relevance, and improvements.

        Resume:
        {resume_text}

        Job Description:
        {job_description}
        """

        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)

        st.markdown("## Audit Report")
        st.markdown(response.text)
