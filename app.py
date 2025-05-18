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
        /* Dark theme colors */
        :root {
            --bg-color: #1E1E1E;
            --text-color: #E0E0E0;
            --primary-color: #7289DA;
            --secondary-color: #4E5D94;
            --accent-color: #99AAB5;
            --success-color: #43B581;
            --warning-color: #FAA61A;
            --error-color: #F04747;
            --card-bg: #2C2F33;
            --border-color: #40444B;
        }

        /* Main container */
        .main {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: var(--primary-color) !important;
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
            text-shadow: 0 0 10px rgba(114, 137, 218, 0.3);
        }
        h2 {
            color: var(--accent-color) !important;
            font-size: 2rem !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
        }
        h3 {
            color: var(--text-color) !important;
            font-size: 1.6rem !important;
            margin-top: 1.5rem !important;
        }
        
        /* Custom containers */
        .info-box {
            background-color: var(--card-bg);
            border-left: 5px solid var(--primary-color);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0.8rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .success-box {
            background-color: rgba(67, 181, 129, 0.1);
            border-left: 5px solid var(--success-color);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0.8rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .warning-box {
            background-color: rgba(250, 166, 26, 0.1);
            border-left: 5px solid var(--warning-color);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 0.8rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            font-weight: 600;
            padding: 0.8rem 2.5rem;
            border-radius: 0.8rem;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
        }
        
        /* File uploader */
        .uploadedFile {
            border: 2px dashed var(--primary-color);
            border-radius: 0.8rem;
            padding: 1.5rem;
            margin: 1.5rem 0;
            background-color: var(--card-bg);
            transition: all 0.3s ease;
        }
        
        .uploadedFile:hover {
            border-color: var(--accent-color);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            background-color: var(--card-bg);
            border-radius: 0.8rem;
            overflow: hidden;
        }
        th {
            background-color: var(--secondary-color);
            color: var(--text-color);
            padding: 1rem;
            text-align: left;
        }
        td {
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-color);
        }
        tr:hover {
            background-color: rgba(114, 137, 218, 0.1);
        }
        
        /* Feedback sections */
        .feedback-section {
            background-color: var(--card-bg);
            padding: 2rem;
            border-radius: 0.8rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        }
        
        /* Input fields */
        .stTextInput input {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
            border-radius: 0.8rem !important;
            padding: 0.8rem 1rem !important;
        }
        
        .stTextInput input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(114, 137, 218, 0.2) !important;
        }
        
        /* Spinner */
        .stSpinner {
            color: var(--primary-color) !important;
        }
        
        /* Footer */
        .footer {
            margin-top: 4rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: var(--accent-color);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-color);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--secondary-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* Global text */
        p, li, span {
            color: var(--text-color);
        }
        
        /* Links */
        a {
            color: var(--primary-color);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        a:hover {
            color: var(--accent-color);
            text-decoration: underline;
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
- Avoid passive or vague phrases like "Worked on" or "Helped with."
  
**Use this format:**

❌ *[Original bullet from resume]*  

✅ *[Improved version using action verb, clarity, and result]*

**Deep Fix (3–5 hrs):**  
- Reframe each experience to show outcomes and impact. Use the **[Action] + [What you did] + [Result]** format.  
- Add quantifiable metrics (e.g., "increased sales by 15%," "managed budget of $10K").  
- Tailor descriptions to reflect competencies relevant to the target role or industry.

---

### 🎨 Design

**Quick Fix (≤1 hr):**  
- Use consistent fonts, spacing, and alignment.  
- Make sure section headers are clear and bold, and that margins are not cramped.

**Example (based on resume):**  

❌ *Multiple font sizes used in 'Experience' section*

✅ *Use one consistent font (e.g., Calibri 11pt) and align all bullets to left*

**Deep Fix (3–5 hrs):**  
- Apply a modern, ATS-friendly layout (e.g., left-aligned layout, no columns or graphics).  
- Use section hierarchy (Summary → Skills → Experience → Education → Projects).  
- Remove clutter like icons, photos, or complex visual elements that confuse ATS parsing.

---

### 🎯 Strategy

**Quick Fix (≤1 hr):**  
- Add 4–6 keywords from a relevant job description (skills, tools, roles).
- Rewrite your summary to clearly state your goal and top strengths.

**Use this format:**

❌ *[Original summary from resume]*  

✅ *[Improved version with clearer career goals and targeted language]*

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

- **No AI disclaimers** (e.g., "As an AI...", "Good luck...").
- **No filler or vague praise** (e.g., "Great job!", "Looks good.").
- **Stay in character** as a senior hiring manager with 20+ years in {job_field}.
- **Be direct, professional, and role-specific**.
- **All feedback must be specific and actionable** (e.g., include revised bullet points, layout advice, keyword suggestions).
- **Do not explain your process or how you generated the feedback**.
- **Focus only on resume effectiveness, ATS performance, and alignment to {job_field} roles**.

💡 *Final Reminder:*  
Your output will be discarded if it includes:
- AI disclaimers  
- Fluff, encouragement, or "as an AI" language  
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
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Resume Audit Pro - AI-powered resume analysis tool"
        }
    )
    
    # Apply custom CSS
    local_css()
    
    # Set dark theme
    st.markdown("""
        <script>
            var observer = new MutationObserver(function(mutations) {
                document.body.style.backgroundColor = '#1E1E1E';
            });
            observer.observe(document.body, { attributes: true });
        </script>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Header section with modern layout
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>📄 Resume Audit Pro</h1>
            <div class='info-box' style='max-width: 800px; margin: 2rem auto;'>
                <h3 style='margin-top: 0;'>Professional Resume Analysis</h3>
                <p>Get expert feedback on your resume with our AI-powered analysis tool. 
                We evaluate your resume for:</p>
                <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;'>
                    <div>✨ ATS Compatibility</div>
                    <div>📊 Content Strength</div>
                    <div>🎯 Industry Alignment</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for the main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Step 1: File Upload
        st.markdown("""
            <div class='feedback-section'>
                <h2 style='margin-top: 0;'>📤 Upload Your Resume</h2>
                <p>Upload your resume in PDF format for a comprehensive analysis.</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf", label_visibility="collapsed")
        
        if uploaded_file:
            if uploaded_file.name != st.session_state.last_uploaded_filename:
                st.session_state.last_uploaded_filename = uploaded_file.name
                st.session_state.resume_text = None
                st.session_state.feedback = None
                st.session_state.analyze_clicked = False
            
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
                <div class='feedback-section'>
                    <h2 style='margin-top: 0;'>🎯 Specify Target Role</h2>
                    <p>Enter the job title or field you're targeting to receive tailored feedback.</p>
                </div>
            """, unsafe_allow_html=True)
            
            job_field = st.text_input(
                "Enter job title or field",
                placeholder="e.g., Software Engineer, Data Scientist, Marketing Manager",
                label_visibility="collapsed"
            )
            
            # Step 3: Audit Button
            st.markdown("""
                <div class='feedback-section'>
                    <h2 style='margin-top: 0;'>🔍 Run Analysis</h2>
                    <p>Click the button below to get detailed feedback on your resume.</p>
                </div>
            """, unsafe_allow_html=True)

            if 'analyze_clicked' not in st.session_state:
                st.session_state.analyze_clicked = False
            
            if st.button("Analyze Resume", use_container_width=True, key="analyze_button"):
                st.session_state.analyze_clicked = True
            
            if st.session_state.analyze_clicked:
                if not job_field:
                    st.markdown("""
                        <div class='warning-box'>
                            ❌ Please enter the job field you're applying for.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
                    st.stop()
                
                if time() - st.session_state.last_time < COOLDOWN:
                    st.markdown("""
                        <div class='warning-box'>
                            ⏳ Please wait a moment before running another analysis.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
                    st.stop()
                
                with st.spinner("🧠 Analyzing your resume..."):
                    feedback = get_resume_feedback(st.session_state.resume_text, job_field)
                    if not feedback:
                        st.markdown("""
                            <div class='warning-box'>
                                🤖 Analysis failed. Please try again.
                            </div>
                        """, unsafe_allow_html=True)
                        st.session_state.analyze_clicked = False
                        st.stop()
                    
                    st.session_state.feedback = feedback
                    st.session_state.last_time = time()
                    
                    st.markdown("""
                        <div class='success-box'>
                            ✅ Analysis complete! See detailed feedback below.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
    
    # Display feedback in a clean, modern layout
    if st.session_state.feedback:
        st.markdown("""
            <div class='feedback-section' style='margin-top: 3rem;'>
                <h2 style='margin-top: 0; text-align: center;'>📝 Resume Evaluation Results</h2>
                <div style='margin-top: 2rem;'>
        """, unsafe_allow_html=True)
        
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Modern footer with social links
    st.markdown("""
        <div class='footer'>
            <div style='margin-bottom: 1rem;'>
                📝 Created by Aman Ghuman
            </div>
            <div style='font-size: 0.9rem;'>
                Resume Audit Pro - Your AI-powered resume analysis tool
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
