# app.py

import streamlit as st
import pdfplumber
import os
import google.generativeai as genai
from dotenv import load_dotenv
from time import time

genai.configure(api_key=st.secrets.gemini.api_key)

MAX_TEXT_LENGTH = 100_000
COOLDOWN = 2

def init_session_state():
    """Initialize session state variables"""
    if "last_time" not in st.session_state:
        st.session_state.last_time = 0
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = None
    if "last_uploaded_filename" not in st.session_state:
        st.session_state.last_uploaded_filename = None

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip() if text.strip() else None
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

def get_resume_feedback(resume_text, job_field):
    """Get Feedback on resume"""
    prompt = f"""
# 📄 Resume Review Prompt for {job_field} Position

You are a **senior hiring manager** with over 20 years of experience at top-tier global companies, specifically in {job_field}.  
Your task is to critically evaluate the resume provided below as if you're deciding whether to shortlist this candidate for a competitive {job_field} role.

Your feedback should be **professional, practical, and tailored for a real-world job search in {job_field}**.  
Focus on **clarity, structure, tone, formatting, keyword alignment**, and **overall impact**—with an eye on how well this resume would perform both with human recruiters and Applicant Tracking Systems (ATS).

---

## 📝 Resume Evaluation

- **Current Effectiveness (1–10):**
- **Optimized Potential (1–10):**
- **Brief Summary of Strengths & Issues:**
- **ATS Readiness (Yes/No):**
- **Your Key Takeaway (1–2 sentences):**

---

## 🚨 Major Issues (Red Flags)

List critical issues that could hurt the resume's chances, along with suggestions for improvement.  
Each issue should include an **example of the original content** and a **revised version**, specifically for {job_field} positions.

| Issue                       | Original Example                                      | Improved Example                                      |
|----------------------------|-------------------------------------------------------|--------------------------------------------------------|
| Vague Bullet Point         | "Worked on team projects"                             | "Collaborated with 4-person team to develop a web app used by 200+ students" |
| Weak Action Verb           | "Responsible for social media"                        | "Managed and grew Instagram following by 30% in 3 months" |
| No Quantifiable Impact     | "Helped with data entry"                              | "Entered and verified 1,200+ records with 99.8% accuracy over 2 months" |
| Irrelevant Information     | "High school science fair winner" (on college resume) | — *(Remove if not relevant to job or recent)*          |
| Unclear Layout             | Mixed fonts, inconsistent spacing                     | Use a clean, consistent layout with clear section headers |


---

## ⚙️ ATS Compatibility Check for {job_field}

- **Missing or Weak Keywords:**  
- **Design/Layout Barriers:**  
- **Estimated ATS Score (1–10):**

---

## 🔧 Fix Recommendations

| Category   | Quick Fix (≤1 hr)                          | Deep Fix (3–5 hrs)                          |
|------------|--------------------------------------------|---------------------------------------------|
| **Content** | Sharpen bullet points, add action verbs    | Rework descriptions to show results         |
| **Design**  | Standardize fonts, improve spacing         | Apply modern, clean professional layout     |
| **Strategy**| Add relevant keywords, tighten summary     | Tailor resume to specific job goals         |

---

## 🎯 Positioning Benchmark for {job_field}

- **Target Level:** (e.g., Internship / Entry-Level / Mid-Level)
- **Resume Tier:** Top 10% / Average / Needs Work
- **One-Line Summary:** (e.g., "Strong foundation, needs polish for ATS and visual clarity.")

---

## ✅ Key {job_field} Industry Tips

- Keep it to one page unless you have over 5 years of experience.
- Prioritize results and impact (quantify wherever possible).
- Align language and structure with {job_field} job descriptions.
- Avoid overly designed templates—ATS may not parse them well.
- Proofread for grammar, consistency, and tone.
- Include specific {job_field} technical skills and certifications.

---

Resume:
\"\"\"
{resume_text[:MAX_TEXT_LENGTH]}
\"\"\"
"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini Error: {e}")
        return None

def main():
    st.set_page_config(page_title="Resume Audit Pro", page_icon="📄", layout="wide")
    st.title("📄 Resume Audit Pro")
    
    # Initialize session state
    init_session_state()
    
    # File upload
    uploaded_file = st.file_uploader("📤 Upload Resume (PDF only)", type="pdf")
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.session_state.resume_text = None
            st.session_state.feedback = None
        
        # Extract text from PDF
        if not st.session_state.resume_text:
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text:
                st.error("❌ Couldn't extract text from PDF.")
                st.stop()
            st.session_state.resume_text = resume_text
            st.success("✅ Resume uploaded successfully!")
        
        # Job field input
        job_field = st.text_input("🎯 Enter the job title or field you're applying for:", 
                                 placeholder="e.g., Software Engineer, Data Scientist, Marketing Manager")
        
        # Audit button
        if st.button("🔍 Audit Resume"):
            if not job_field:
                st.error("❌ Please enter the job field you're applying for.")
                st.stop()
            
            if time() - st.session_state.last_time < COOLDOWN:
                st.warning("⏳ Please wait a moment before running another audit.")
                st.stop()
            
            with st.spinner("🧠 Analyzing your resume..."):
                feedback = get_resume_feedback(st.session_state.resume_text, job_field)
                if not feedback:
                    st.error("🤖 Audit failed.")
                    st.stop()
                
                st.session_state.feedback = feedback
                st.session_state.last_time = time()
                
                st.success("✅ Audit complete!")
    
    # Display feedback
    if st.session_state.feedback:
        st.markdown("## 🔍 AI Resume Feedback")
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
    
    # Footer
    st.markdown("---")
    st.markdown("📝 Created by [Aman Ghuman]")#(https://twitter.com/kaiweng) | [GitHub](https://github.com/kaiweng/resume-audit-pro)")

if __name__ == "__main__":
    main()

