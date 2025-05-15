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

# Custom CSS
def local_css():
    st.markdown("""
    <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: #1E88E5;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
        }
        h2 {
            color: #0D47A1;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
        }
        h3 {
            color: #1565C0;
            font-size: 1.4rem !important;
            margin-top: 1.5rem !important;
        }
        
        /* Custom containers */
        .info-box {
            background-color: #E3F2FD;
            border-left: 5px solid #1E88E5;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        .success-box {
            background-color: #E8F5E9;
            border-left: 5px solid #43A047;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        .warning-box {
            background-color: #FFF3E0;
            border-left: 5px solid #FB8C00;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #1E88E5;
            color: white;
            font-weight: 600;
            padding: 0.5rem 2rem;
            border-radius: 0.5rem;
            border: none;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #1565C0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        /* File uploader */
        .uploadedFile {
            border: 2px dashed #1E88E5;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        th {
            background-color: #E3F2FD;
            padding: 0.75rem;
            text-align: left;
        }
        td {
            padding: 0.75rem;
            border-top: 1px solid #E0E0E0;
        }
        
        /* Feedback sections */
        .feedback-section {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin: 1.5rem 0;
        }
        
        /* Footer */
        .footer {
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #E0E0E0;
            text-align: center;
            color: #757575;
        }
    </style>
    """, unsafe_allow_html=True)

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

⚠️ **Format Required**  
Respond using the *exact* section titles, formatting, and Markdown structure as shown below.  
**Do not skip or add sections. Do not reword headings.**

- **Current Effectiveness (1–10):** 6  
- **Optimized Potential (1–10):** 8  
- **Brief Summary of Strengths & Issues:** Strong technical base, but layout and phrasing limit clarity.  
- **ATS Readiness (Yes/No):** No  
- **Your Key Takeaway (1–2 sentences):** Needs reformatting and stronger action verbs to stand out in ATS and recruiter review.


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

Below are quick and deep fixes across three key areas of resume improvement: **Content**, **Design**, and **Strategy**.

### 📌 Content

**Quick Fix (≤1 hr):**  
- Rewrite bullet points using strong action verbs (e.g., "Led", "Created", "Improved").
- Avoid passive or vague phrases like “Worked on” or “Helped with.”
  
  **Example:**  
  ❌ "Helped with marketing tasks"  
  
  ✅ "Assisted in planning and executing 3 marketing campaigns, increasing engagement by 20%"

**Deep Fix (3–5 hrs):**  
- Reframe each experience to show outcomes and impact. Use the **[Action] + [What you did] + [Result]** format.  
- Add quantifiable metrics (e.g., “increased sales by 15%,” “managed budget of $10K”).  
- Tailor descriptions to reflect competencies relevant to the target role or industry.

---

### 🎨 Design

**Quick Fix (≤1 hr):**  
- Use consistent fonts, spacing, and alignment.  
- Make sure section headers are clear and bold, and that margins are not cramped.

**Example:**  
❌ Multiple font types and sizes

✅ One clean, readable font (e.g., Calibri or Helvetica), consistent size (11–12pt), clear spacing

**Deep Fix (3–5 hrs):**  
- Apply a modern, ATS-friendly layout (e.g., left-aligned layout, no columns or graphics).  
- Use section hierarchy (Summary → Skills → Experience → Education → Projects).  
- Remove clutter like icons, photos, or complex visual elements that confuse ATS parsing.

---

### 🎯 Strategy

**Quick Fix (≤1 hr):**  
- Add 4–6 keywords from a relevant job description (skills, tools, roles).
- Rewrite your summary to clearly state your goal and top strengths.

  **Example:**  
  ❌ "I am a hard-working individual"
  
  ✅ "Aspiring data analyst with strong Python and Excel skills, seeking to apply data-driven insights to real-world problems."

**Deep Fix (3–5 hrs):**  
- Research 2–3 target job listings and align resume language and structure to match.  
- Prioritize the most relevant experiences—even if not in reverse chronological order.  
- Refine the resume narrative to reflect your career goals and unique value proposition.

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

## ⚠️ Response Constraints (Strict)

- **No AI disclaimers** (e.g., “As an AI...”, “Good luck...”).
- **No filler or vague praise** (e.g., “Great job!”, “Looks good.”).
- **Stay in character** as a senior hiring manager with 20+ years in {job_field}.
- **Be direct, professional, and role-specific**.
- **All feedback must be specific and actionable** (e.g., include revised bullet points, layout advice, keyword suggestions).
- **Do not explain your process or how you generated the feedback**.
- **Focus only on resume effectiveness, ATS performance, and alignment to {job_field} roles**.

💡 *Final Reminder:*  
Your output will be discarded if it includes:
- AI disclaimers  
- Fluff, encouragement, or “as an AI” language  
- Skipped sections or altered headings

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
    st.set_page_config(
        page_title="Resume Audit Pro",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom CSS
    local_css()
    
    # Initialize session state
    init_session_state()
    
    # Header section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>📄 Resume Audit Pro</h1>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
            Get professional feedback on your resume with AI-powered analysis. 
            Our tool evaluates your resume for ATS compatibility, content strength, and industry alignment.
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Step 1: File Upload
    st.markdown("""
    <h2>📤 Step 1: Upload Your Resume</h2>
    <p>Upload your resume in PDF format for analysis.</p>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf", label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name
            st.session_state.resume_text = None
            st.session_state.feedback = None
            st.session_state.analyze_clicked = False  # Reset analyze button state
        
        # Extract text from PDF
        if not st.session_state.resume_text:
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text:
                st.markdown("""
                <div class='warning-box'>
                    ❌ Could not extract text from PDF. Please ensure your PDF contains selectable text.
                </div>
                """, unsafe_allow_html=True)
                st.stop()
            st.session_state.resume_text = resume_text
            st.markdown("""
            <div class='success-box'>
                ✅ Resume uploaded successfully!
            </div>
            """, unsafe_allow_html=True)
        
        # Step 2: Job Field Input
        st.markdown("""
        <h2>🎯 Step 2: Specify Target Role</h2>
        <p>Enter the job title or field you're applying for to receive tailored feedback.</p>
        """, unsafe_allow_html=True)
        
        job_field = st.text_input(
            "Enter job title or field",
            placeholder="e.g., Software Engineer, Data Scientist, Marketing Manager",
            label_visibility="collapsed"
        )
        
        # Step 3: Audit Button
        st.markdown("""
        <h2>🔍 Step 3: Run Analysis</h2>
        <p>Click the button below to analyze your resume.</p>
        """, unsafe_allow_html=True)

        # Initialize analyze_clicked in session state if it doesn't exist
        if 'analyze_clicked' not in st.session_state:
            st.session_state.analyze_clicked = False
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Analyze Resume", use_container_width=True, key="analyze_button"):
                st.session_state.analyze_clicked = True
        
        if st.session_state.analyze_clicked:
            if not job_field:
                st.markdown("""
                <div class='warning-box'>
                    ❌ Please enter the job field you're applying for.
                </div>
                """, unsafe_allow_html=True)
                st.session_state.analyze_clicked = False  # Reset the button state
                st.stop()
            
            if time() - st.session_state.last_time < COOLDOWN:
                st.markdown("""
                <div class='warning-box'>
                    ⏳ Please wait a moment before running another analysis.
                </div>
                """, unsafe_allow_html=True)
                st.session_state.analyze_clicked = False  # Reset the button state
                st.stop()
            
            with st.spinner("🧠 Analyzing your resume..."):
                feedback = get_resume_feedback(st.session_state.resume_text, job_field)
                if not feedback:
                    st.markdown("""
                    <div class='warning-box'>
                        🤖 Analysis failed. Please try again.
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False  # Reset the button state
                    st.stop()
                
                st.session_state.feedback = feedback
                st.session_state.last_time = time()
                
                st.markdown("""
                <div class='success-box'>
                    ✅ Analysis complete! See detailed feedback below.
                </div>
                """, unsafe_allow_html=True)
                st.session_state.analyze_clicked = False  # Reset for next analysis
    
    # Display feedback
    if st.session_state.feedback:
        #st.markdown("<div class='feedback-section'>", unsafe_allow_html=True)
        st.markdown("## 📝 Resume Evaluation")
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        📝 Created by <a href='https://twitter.com/kaiweng'>Aman Ghuman</a> | 
        <a href='https://github.com/kaiweng/resume-audit-pro'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
