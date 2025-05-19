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

## 🎯 Analysis Framework

Evaluate the resume across these key dimensions:
1. **ATS Optimization** - Compatibility with Applicant Tracking Systems
2. **Content Quality** - Strength and impact of achievements
3. **Industry Alignment** - Relevance to {job_field}
4. **Visual Structure** - Layout and formatting effectiveness

## 📊 Scoring Criteria

Rate each aspect on a scale of 1-10:
- 1-3: Needs significant improvement
- 4-6: Meets basic requirements
- 7-8: Strong performance
- 9-10: Exceptional

## 📝 Required Response Format

### 1. Executive Summary
- **Current Resume Score:** [1-10]
- **Potential Score After Improvements:** [1-10]
- **Key Strengths:** [3 bullet points]
- **Critical Gaps:** [3 bullet points]
- **ATS Readiness:** [Yes/No]

### 2. 🚨 Priority Improvements
List 3-5 critical issues that need immediate attention:

| Issue | Current State | Recommended Improvement | Impact |
|-------|--------------|------------------------|---------|
| [Issue 1] | [Example] | [Better Version] | [Expected Outcome] |

### 3. 🎯 Industry-Specific Analysis for {job_field}
- **Missing Keywords:** [List crucial industry terms]
- **Technical Skills Gap:** [Identify missing skills]
- **Experience Alignment:** [How well experience matches industry needs]

### 4. 📈 Detailed Recommendations

#### Content Enhancement
- **Achievement Statements**
  - Before: [Original bullet]
  - After: [Improved version with metrics]
  
- **Skills Presentation**
  - Before: [Current format]
  - After: [Optimized format]

#### Visual Optimization
- **Layout:** [Specific formatting recommendations]
- **Structure:** [Section organization advice]
- **Formatting:** [Typography and spacing suggestions]

### 5. 🔍 ATS Optimization Guide
- **Format Issues:** [List any problematic elements]
- **Keyword Density:** [Analysis of key terms]
- **Parsing Challenges:** [Identify potential ATS issues]

### 6. 🎯 Industry Best Practices for {job_field}
- **Must-Have Elements:** [Essential components]
- **Emerging Trends:** [Current industry preferences]
- **Red Flags:** [What to avoid]

## 💡 Implementation Priority
1. **Immediate Actions** (24 hours):
   - [Action 1]
   - [Action 2]
2. **Short-term Improvements** (1 week):
   - [Improvement 1]
   - [Improvement 2]
3. **Long-term Enhancements** (1 month):
   - [Enhancement 1]
   - [Enhancement 2]

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
