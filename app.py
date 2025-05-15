# app.py

import streamlit as st
import pdfplumber
import os
import google.generativeai as genai
from time import time
import json
from requests_oauthlib import OAuth2Session

genai.configure(api_key=st.secrets.gemini.api_key)

GOOGLE_CLIENT_ID = st.secrets.google.client_id
GOOGLE_CLIENT_SECRET = st.secrets.google.client_secret
REDIRECT_URI = "https://resume-audit-pro.streamlit.app/"

MAX_TEXT_LENGTH = 100_000
COOLDOWN = 2
TOKEN_FILE = "users.json"

# --- Google OAuth Setup ---
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

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

def load_user_tokens():
    """Load or initialize user tokens"""
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "w") as f:
            json.dump({}, f)
    
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save user data to file"""
    with open(TOKEN_FILE, "w") as f:
        json.dump(users, f, indent=2)

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip() if text.strip() else None
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

def get_resume_feedback(resume_text):
    """Get AI feedback on resume"""
    prompt = f"""
# 📄 Resume Review Prompt

You are a **senior hiring manager** with over 20 years of experience at top-tier global companies.  
Your task is to critically evaluate the resume provided below as if you're deciding whether to shortlist this candidate for a competitive role.

Your feedback should be **professional, practical, and tailored for a real-world job search**.  
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

List critical issues that could hurt the resume’s chances, along with suggestions for improvement.  
Each issue should include an **example of the original content** and a **revised version**.

| Issue                       | Original Example                                      | Improved Example                                      |
|----------------------------|-------------------------------------------------------|--------------------------------------------------------|
| Vague Bullet Point         | "Worked on team projects"                             | "Collaborated with 4-person team to develop a web app used by 200+ students" |
| Weak Action Verb           | "Responsible for social media"                        | "Managed and grew Instagram following by 30% in 3 months" |
| No Quantifiable Impact     | "Helped with data entry"                              | "Entered and verified 1,200+ records with 99.8% accuracy over 2 months" |
| Irrelevant Information     | "High school science fair winner" (on college resume) | — *(Remove if not relevant to job or recent)*          |
| Unclear Layout             | Mixed fonts, inconsistent spacing                     | Use a clean, consistent layout with clear section headers |


---

## ⚙️ ATS Compatibility Check

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

## 🎯 Positioning Benchmark

- **Target Level:** (e.g., Internship / Entry-Level / Mid-Level)
- **Resume Tier:** Top 10% / Average / Needs Work
- **One-Line Summary:** (e.g., “Strong foundation, needs polish for ATS and visual clarity.”)

---

## ✅ Suggestions for Improvement (General Tips for Students)

- Keep it to one page unless you have over 5 years of experience.
- Prioritize results and impact (quantify wherever possible).
- Align language and structure with job descriptions.
- Avoid overly designed templates—ATS may not parse them well.
- Proofread for grammar, consistency, and tone.

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
        st.error(f"IE: {e}")
        return None

def main():
    st.set_page_config(page_title="Resume Audit Pro", page_icon="📄", layout="wide")
    st.title("📄 Resume Audit Pro")
    
    # Initialize session state
    init_session_state()
    
    # Load user data
    users = load_user_tokens()
    user_email = None
    
    # Handle Google OAuth
    if "auth_code" not in st.session_state:
        oauth = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
        authorization_url, state = oauth.authorization_url(AUTHORIZATION_BASE_URL, access_type="offline", prompt="select_account")
        st.markdown(f"[🔐 Sign in with Google]({authorization_url})")
        
        if "code" in st.query_params:
            st.session_state.auth_code = st.query_params["code"]
    
    if "auth_code" in st.session_state and not st.session_state.get("access_token"):
        oauth = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
        token = oauth.fetch_token(
            TOKEN_URL,
            client_secret=GOOGLE_CLIENT_SECRET,
            code=st.session_state.auth_code
        )
        st.session_state.access_token = token["access_token"]
    
    # Get user info if logged in
    if st.session_state.get("access_token"):
        import requests
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        profile = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers).json()
        user_email = profile["email"]
        user_name = profile.get("name", "User")
        
        st.success(f"👋 Welcome {user_name}")
        if user_email not in users:
            users[user_email] = {"tokens": 3, "name": user_name}
            save_users(users)
        st.markdown(f"🎟️ Tokens Remaining: `{users[user_email]['tokens']}`")
    
    # File upload and processing
    uploaded_file = st.file_uploader("📤 Upload Resume (PDF only)", type="pdf")
    
    if uploaded_file:
        if time() - st.session_state.last_time < COOLDOWN:
            st.warning("⏳ Wait before next submission")
            st.stop()
        
        if uploaded_file.name != st.session_state.last_uploaded_filename:
            st.session_state.last_uploaded_filename = uploaded_file.name
        
        with st.spinner("🧠 Auditing..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text:
                st.error("❌ Couldn't extract text.")
                st.stop()
            
            feedback = get_resume_feedback(resume_text)
            if not feedback:
                st.error("🤖 Audit failed.")
                st.stop()
            
            st.session_state.resume_text = resume_text
            st.session_state.feedback = feedback
            st.session_state.last_time = time()
            
            st.success("✅ Audit complete!")
    
    # Display feedback
    if st.session_state.feedback:
        st.markdown("## 🔍 Resume Feedback")
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
    
    # Footer
    st.markdown("---")
    st.markdown("📝 Created by [Aman Ghuman]")#(https://twitter.com/kaiweng) | [GitHub](https://github.com/kaiweng/resume-audit-pro) | [Buy Tokens](/buy)"

if __name__ == "__main__":
    main()
