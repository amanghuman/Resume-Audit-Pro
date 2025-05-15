# app.py

import streamlit as st
import pdfplumber
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
# Executive Resume Audit: Strategic Optimization Framework  
**Role:** Senior Talent Strategist (20+ Years at Global Enterprises)  
**Objective:** Convert resumes into interview-winning documents through ATS precision and executive narrative design  

---

## 📊 Performance Dashboard  
| Metric                | Current Status | Target   | Priority Focus Areas       |  
|-----------------------|----------------|----------|----------------------------|  
| ATS Compliance        | 68/100         | 95+      | Missing core headers       |  
| Human Scan Retention  | 2.1s           | 5s+      | Weak opening hook          |  
| Achievement Ratio     | 41%            | 80%+     | Overemphasis on duties     |  
| Strategic Mirroring   | Limited        | Exact    | JD keywords not integrated |  

---

## ❗ Critical Risks (Immediate Action Required)  
1. **Value Obscurity**  
   - Career-defining achievements buried beneath routine tasks  
   - No quantifiable business impact in 89% of role descriptions  

2. **ATS Rejection Triggers**  
   - Non-standard section titles ("Professional Journey" vs "Experience")  
   - 7/10 required skills from JD missing in first page  

3. **Career Narrative Gaps**  
   - Unexplained 11-month gap formatted as generic consulting period  
   - Progressive leadership story fragmented across roles  

---

## 🔎 ATS Optimization Analysis  
| Compliance Factor     | Status         | Evidence                  |  
|-----------------------|----------------|---------------------------|  
| Keyword Integration   | 42% Match      | "Digital Transformation" missing (JD mentions x6) |  
| Section Integrity     | High Risk      | Mixed date formats (MM/YYYY vs YYYY-MM) |  
| Parse Success Rate     | 51%            | Graphics cause header failure in Greenhouse test |  
| Readability Score     | 3.8/5          | Dense text blocks reduce skimmability |  

---

## 🛠️ Optimization Roadmap  
| Focus Area          | Quick Adjustments (<1hr)      | Strategic Enhancements (2-4hr)     | Competitive Differentiators (5hr+)    |  
|---------------------|-------------------------------|-------------------------------------|---------------------------------------|  
| **Value Proposition** | Add 3 metrics-driven opening bullets | Build CAR (Challenge-Action-Result) narratives | Create JD-specific achievement matrix |  
| **ATS Foundation**  | Standardize all section headers | Weave 5 JD keywords into summary    | Develop multi-version tracking system |  
| **Visual Strategy** | Single-column reformatting    | Implement Z-pattern hierarchy       | Add interactive elements for digital  |  
| **Career Story**    | Clarify employment timeline    | Show promotion velocity with impact  | Integrate leadership philosophy       |  

---

## 🏅 Success Benchmarks  
**Top 1% Resume Standards:**  
- 5-Second Hook: "Drove $560M revenue growth through..."  
- ATS Armor: 100% keyword match in first page  
- Executive Fluency: EBITDA/ROI/NPV alignment  
- Retention Engineering: 8s+ average human scan time  

---

## 📌 Implementation Toolkit  
1. **Achievement Extraction Protocol**  
   - Convert "Managed projects" → "Delivered 22% cost savings across 14 projects..."  
2. **JD Mirroring Technique**  
   - Embed 3 company values into professional summary  
3. **Gap Resolution Framework**  
   - Reframe career break: "Led AI certification program during industry transition"  

---

## 🚩 Red Flag Mitigation  
**Issue:** Multiple short-term roles (2020-2022)  
**Solution:** Cluster as "Turnaround Consultations: Rescued $17M contract for Fortune 500 client"  

**Issue:** Missing executive keywords  
**Solution:** Insert "P&L Leadership" and "Global Scaling" in first 3 bullet points  

---

**Delivery Standards:**  
- Clean markdown structure (no code blocks)  
- Data-first insights with actionable tiers  
- Boardroom-level strategic framing  

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
        st.markdown("## 🔍 AI Resume Feedback")
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
    
    # Footer
    st.markdown("---")
    st.markdown("📝 Created by [Aman Ghuman]")#(https://twitter.com/kaiweng) | [GitHub](https://github.com/kaiweng/resume-audit-pro) | [Buy Tokens](/buy)"

if __name__ == "__main__":
    main()
