import streamlit as st
import pdfplumber
import google.generativeai as genai
from time import time

# Configuration
genai.configure(api_key=st.secrets.gemini.api_key)
MAX_TEXT_LENGTH = 100_000
COOLDOWN = 2


def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

        html, body, .main {
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3 {
            font-weight: 600;
            color: #111827;
        }

        .stButton button {
            background-color: #111827;
            color: white;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
        }

        .stButton button:hover {
            background-color: #374151;
        }

        .feedback-box {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            padding: 2rem;
            border-radius: 12px;
            margin-top: 2rem;
        }

        .ats-bar {
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .success-box, .warning-box {
            background-color: #ecfdf5;
            padding: 1rem;
            border-left: 4px solid #10b981;
            border-radius: 6px;
            margin-top: 1rem;
            color: #065f46;
        }

        .warning-box {
            background-color: #fef3c7;
            border-left-color: #f59e0b;
            color: #92400e;
        }
    </style>
    """, unsafe_allow_html=True)


def init_session():
    if "last_time" not in st.session_state:
        st.session_state.last_time = 0
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "analyze_clicked" not in st.session_state:
        st.session_state.analyze_clicked = False


def extract_pdf_text(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages).strip()
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None


def get_feedback(resume_text, job_field):
    """Get Feedback on resume"""
    prompt = f"""
# 📄 Professional Resume Analysis for {job_field} Position

You are a **senior hiring manager and industry expert** with extensive experience in {job_field}. Your task is to provide a comprehensive, actionable evaluation of the candidate's resume for a {job_field} position.

Create a resume analysis framework using the following structure:

Advanced Resume Optimization Framework
Core Evaluation Dimensions

ATS Compliance

Keyword density and placement

File format and parsing success

Section recognition accuracy

Strategic Content

Quantified achievements (financial, percentage, or scale metrics)

Skill-context alignment

Value proposition clarity

Industry Relevance

Technical terminology usage

Emerging trend awareness

Regulatory/compliance alignment

Visual Hierarchy

Information flow logic

Content density balance

Cross-device rendering consistency

Scoring System

Weighted scoring (1-10 scale):
ATS Compliance (30%), Strategic Content (40%), Industry Relevance (20%), Visual Hierarchy (10%)

Score tiers:
1-4 = Critical gaps | 5-7 = Baseline competitive | 8-10 = Market-leading

Response Structure Requirements

Executive Summary

Current composite score with dimension breakdown

Improvement potential percentage

Top 3 strengths and critical gaps

Priority Improvements Table

Format:
| Issue | Current State | Optimization | Impact Value |
|-------|---------------|--------------|--------------|

Industry-Specific Analysis

List missing mandatory keywords for {job_field}

Identify emerging competency gaps

Provide before/after examples for experience reframing

Technical Recommendations

Achievement statement transformations with metrics

Skills section restructuring examples

Typography and layout standards

ATS Optimization Checklist

Required formatting fixes

Keyword density targets

File format specifications

Industry Benchmarking Data

Top performer differentiators for {job_field}

Common pitfalls to avoid

Implementation Guidelines

Phased timeline: 48-hour fixes, 1-week optimizations, 1-month enhancements

Include measurable impact projections for each recommendation

Use specific before/after comparisons for all suggested changes

Focus on {job_field} standards and keyword requirements

Output Rules

Maintain formal, technical tone

Prioritize quantifiable improvements

Reference current industry hiring trends

Avoid subjective language

Structure all feedback as actionable steps

Resume to analyze:
\"\"\"
{resume_text[:MAX_TEXT_LENGTH]}
\"\"\"

## ⚠️ Response Guidelines
- Maintain professional tone
- Provide specific, actionable feedback
- Include measurable improvements
- Focus on {job_field} industry standards
- Use clear before/after examples
"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None


def main():
    st.set_page_config("Resume Audit Pro", layout="centered", page_icon="📄")
    inject_custom_css()
    init_session()

    st.title("📄 Resume Audit Pro")
    st.caption("AI-powered resume feedback tailored to your target role")

    uploaded_file = st.file_uploader("Upload PDF Resume", type="pdf")

    if uploaded_file:
        resume_text = extract_pdf_text(uploaded_file)
        if not resume_text:
            st.error("Unable to extract text. Please upload a text-based PDF.")
            return
        st.session_state.resume_text = resume_text
        st.success("Resume uploaded successfully.")

        job_field = st.text_input("Target Role", placeholder="e.g., Product Manager, Data Scientist")

        if st.button("Analyze Resume"):
            if not job_field:
                st.warning("Please specify a target role.")
                return

            if time() - st.session_state.last_time < COOLDOWN:
                st.warning("Please wait before running another analysis.")
                return

            with st.spinner("Analyzing..."):
                feedback = get_feedback(resume_text, job_field)
                if feedback:
                    st.session_state.feedback = feedback
                    st.session_state.last_time = time()
                    st.session_state.analyze_clicked = True

    if st.session_state.feedback:
        st.markdown("## ✨ Resume Feedback")
        st.markdown(f"""<div class='feedback-box'>{st.session_state.feedback}</div>""", unsafe_allow_html=True)

        # ATS Progress Example (placeholder logic — you can refine with real scoring later)
        st.markdown("### 📊 ATS Compatibility Score")
        st.progress(0.82)

    st.markdown("---")
    st.caption("Resume Audit Pro © 2024 — AI Feedback, Real Impact.")


if __name__ == "__main__":
    main()
