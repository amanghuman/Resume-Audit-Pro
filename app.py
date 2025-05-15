# app.py

import streamlit as st
import pdfplumber
import os
import google.generativeai as genai
from dotenv import load_dotenv
from time import time
import json
from requests_oauthlib import OAuth2Session

# --- Load Configuration ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"

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
# Resume Optimization Blueprint: Executive-Level Analysis Framework  

**Role:** Chief Talent Architect (20+ Years at Fortune 500/Tech Unicorns)  
**Mission:** Transform resumes into interview-generating assets through tactical ATS hacks and executive storytelling  

---

## 🔍 Performance Dashboard  
| Metric                | Current | Target | Gap Analysis       |  
|-----------------------|---------|--------|--------------------|  
| ATS Parse Score       | 72/100  | 95+    | Critical headers missing |  
| Human Scan Impact     | 2.8s    | 5s+    | Weak value proposition |  
| Achievement Density   | 38%     | 75%+   | Excessive task lists |  
| Strategic Alignment   | Low     | High   | Missing JD mirroring |  

---

## 🚨 Nuclear-Grade Dealbreakers  
1. **Career Narrative Collapse**  
   - No CEO-style summary showing promotion velocity  
   - Impact buried under responsibility lists  

2. **ATS Poison Pill**  
   - Graphics-laden header failing parser tests  
   - Missing 6/8 JD primary keywords  

3. **ROI Black Hole**  
   - 92% of bullets lack metrics/scale context  
   - Zero board-level visibility signals  

---

## ⚡ Threat Intelligence: ATS Kill Zones  
| Risk Factor           | Severity | Evidence            |  
|-----------------------|----------|---------------------|  
| Keyword Starvation    | Critical | "Cloud Migration" x0 vs JD x5 |  
| Section Fragmentation | High     | 3 different "Experience" labels |  
| Parse Survival Rate   | 38%      | Header/font failures in Workday test |  
| Machine Readability   | Poor     | 4 columns break text flow |  

---

## 💼 Boardroom-Grade Optimization Matrix  
| Lever               | Immediate Fix (30m)          | Power Move (3hr)               | Enterprise Play (8hr+)         |  
|---------------------|------------------------------|--------------------------------|--------------------------------|  
| **Value Engine**    | Convert tasks to ROI bullets | Build executive brand story    | Create JD-specific value matrix |  
| **ATS Core**        | Standardize section headers  | Inject JD keywords naturally   | Build multi-JD variant system   |  
| **Visual Hierarchy**| Simplify font stack          | Implement F-pattern layout     | Add skimmable achievement bars |  
| **Credibility Stack**| Add promotions timeline     | Show dollarized impact         | Integrate media/testimonials   |  

---

## 🏆 Fortune 500 Success Signature  
**Top 1% Resume DNA:**  
- 5s Hook: "Generated $2.3B in cloud savings through..."  
- Power Pattern: Challenge > Action > Result (CAR)  
- Board Fluency: EBITDA/OKR/NPV terminology  
- Anti-Fragile Design: Passes 12+ ATS parsers  

---

## 🛠️ Executive Rebuild Kit  
1. **Promotion Velocity Map**  
   - Visual timeline showing role progression + biz impact  
2. **Metric Injection Protocol**  
   - Convert "managed team" → "Led 45-engineer team..."  
3. **JD Assimilation Engine**  
   - Mirror 3 company-specific values in summary  

---

## 🔥 Red Flag Demolition Crew  
**Problem:** 18-month career gap post-COVID  
**Fix:** "Strategic Sabbatical - Led AI upskilling initiative..."  

**Problem:** Multiple <2-year roles  
**Fix:** Cluster as "Consulting Engagements" with client wins  

---

**Delivery Format:**  
- Strict MD tables/headers (NO backticks)  
- Data-driven insights only (NO fluff)  
- C-suite ready terminology  

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
        st.markdown("## 🔍 AI Resume Feedback")
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
    
    # Footer
    st.markdown("---")
    st.markdown("📝 Created by [Aman Ghuman]")#(https://twitter.com/kaiweng) | [GitHub](https://github.com/kaiweng/resume-audit-pro) | [Buy Tokens](/buy)"

if __name__ == "__main__":
    main()
