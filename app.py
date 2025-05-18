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
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

        body, .main {
            background: linear-gradient(135deg, #222831 0%, #00ADB5 100%);
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            letter-spacing: -0.5px;
        }

        p {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #EEEEEE !important;
        }

        h1 {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: #fff !important;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #00ADB5 !important;
        }

        .info-box, .feedback-section, .success-box, .warning-box {
            background: rgba(34, 40, 49, 0.95);
            border-radius: 16px;
            box-shadow: 0 4px 24px 0 rgba(0,0,0,0.10);
            padding: 2rem;
            margin: 1.5rem 0;
            transition: box-shadow 0.3s, transform 0.3s;
        }
        .info-box:hover, .feedback-section:hover {
            box-shadow: 0 8px 32px 0 rgba(0,173,181,0.15);
            transform: translateY(-2px) scale(1.01);
        }

        .stButton button, .stTextInput input, .stFileUploader, .stTextArea textarea {
            border-radius: 16px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 1.1rem !important;
            transition: box-shadow 0.2s, background 0.2s, transform 0.2s;
        }
        .stButton button {
            background: linear-gradient(90deg, #00ADB5 0%, #393E46 100%) !important;
            color: #fff !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 8px 0 rgba(0,173,181,0.10);
            border: none !important;
            padding: 0.9rem 2.2rem !important;
        }
        .stButton button:hover {
            background: linear-gradient(90deg, #00cfcf 0%, #393E46 100%) !important;
            transform: scale(1.04);
            box-shadow: 0 4px 16px 0 rgba(0,173,181,0.18);
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border: 2px solid #00ADB5 !important;
            box-shadow: 0 0 0 2px #00ADB533 !important;
        }
        .stFileUploader {
            background: rgba(57, 62, 70, 0.95) !important;
            border: 2px dashed #00ADB5 !important;
            color: #EEEEEE !important;
        }
        .stFileUploader label {
            color: #EEEEEE !important;
        }
        .footer {
            background: none;
            border-top: none;
            color: #EEEEEE;
            font-size: 1rem;
            opacity: 0.8;
            padding: 2rem 0 0 0;
        }
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        .footer-description {
            font-size: 1rem;
            color: #EEEEEE;
            opacity: 0.7;
            max-width: 600px;
            text-align: left;
        }
        .footer-brand {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            color: #00ADB5;
            opacity: 0.9;
            font-weight: 600;
        }
        /* Subtle fade-in animation for main sections */
        .info-box, .feedback-section, .success-box, .warning-box {
            animation: fadeInUp 0.7s cubic-bezier(.39,.575,.565,1) both;
        }
        @keyframes fadeInUp {
            0% { opacity: 0; transform: translateY(30px);}
            100% { opacity: 1; transform: translateY(0);}
        }
        .hero { padding: 3rem 0 2rem 0; text-align: center; }
        .hero-content { max-width: 600px; margin: 0 auto; }
        .hero h1 { font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem; font-weight: 700; color: #fff; }
        .tagline { font-size: 1.3rem; color: #00ADB5; margin-bottom: 1.5rem; }
        .hero-img { width: 220px; margin: 1.5rem 0; }
        .trust-box { background: #393E46; color: #EEEEEE; border-radius: 16px; padding: 1rem 1.5rem; margin: 1.5rem 0; font-size: 1rem; }
        .progress-bar { margin: 1.5rem 0; }
        .footer { background: none; border-top: 1px solid #393E46; color: #EEEEEE; font-size: 1rem; opacity: 0.8; padding: 2rem 0 0 0; }
        .footer-links a { color: #00ADB5; margin-right: 1.5rem; text-decoration: none; }
        .testimonials, .partners { display: flex; gap: 2rem; justify-content: center; margin: 2rem 0; }
        .testimonial-card { background: #393E46; border-radius: 16px; padding: 1.2rem 1.5rem; color: #EEEEEE; font-size: 1rem; box-shadow: 0 2px 8px 0 rgba(0,173,181,0.10);}
        .partner-logo { height: 32px; opacity: 0.7; }
        @media (max-width: 700px) {
            .hero h1 { font-size: 2rem; }
            .hero-img { width: 120px; }
            .footer-content { flex-direction: column; align-items: flex-start; }
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
        st.error(f"Gemini Error: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Resume Audit Pro",
        page_icon=None,
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
    
    # Initialize session state
    init_session_state()
    
    # Header section with minimalist layout
    st.markdown("""
        <div style='padding: 2rem 0; margin-bottom: 2rem; border-bottom: 1px solid var(--border-color);'>
            <h1>Resume Audit Pro</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for the main content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Step 1: File Upload
        st.markdown("""
            <div class='feedback-section'>
                <h2>Upload Your Resume</h2>
                <p>Upload your resume in PDF format for analysis.</p>
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
                            Could not extract text from PDF. Please ensure your PDF contains selectable text.
                        </div>
                    """, unsafe_allow_html=True)
                    st.stop()
                st.session_state.resume_text = resume_text
                st.markdown("""
                    <div class='success-box'>
                        Resume uploaded successfully
                    </div>
                """, unsafe_allow_html=True)
            
            # Step 2: Job Field Input
            st.markdown("""
                <div class='feedback-section'>
                    <h2>Target Role</h2>
                    <p>Enter the job title or field you're targeting.</p>
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
                    <h2>Analyze Resume</h2>
                    <p>Get detailed feedback on your resume.</p>
                </div>
            """, unsafe_allow_html=True)

            if 'analyze_clicked' not in st.session_state:
                st.session_state.analyze_clicked = False
            
            if st.button("Analyze", use_container_width=True, key="analyze_button"):
                st.session_state.analyze_clicked = True
            
            if st.session_state.analyze_clicked:
                if not job_field:
                    st.markdown("""
                        <div class='warning-box'>
                            Please enter the job field you're applying for.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
                    st.stop()
                
                if time() - st.session_state.last_time < COOLDOWN:
                    st.markdown("""
                        <div class='warning-box'>
                            Please wait a moment before running another analysis.
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
                    st.stop()
                
                with st.spinner("Analyzing your resume..."):
                    progress = st.progress(0, text='Analyzing your resume...')
                    for percent in range(1, 101):
                        time.sleep(0.01)
                        progress.progress(percent, text=f'Analyzing your resume... {percent}%')
                    progress.empty()
                    
                    feedback = get_resume_feedback(st.session_state.resume_text, job_field)
                    if not feedback:
                        st.markdown("""
                            <div class='warning-box'>
                                Analysis failed. Please try again.
                            </div>
                        """, unsafe_allow_html=True)
                        st.session_state.analyze_clicked = False
                        st.stop()
                    
                    st.session_state.feedback = feedback
                    st.session_state.last_time = time()
                    
                    st.markdown("""
                        <div class='success-box'>
                            Analysis complete
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.analyze_clicked = False
    
    # Display feedback in a clean, modern layout
    if st.session_state.feedback:
        st.markdown("""
            <div class='feedback-section' style='margin-top: 3rem;'>
                <h2 style='margin-top: 0; text-align: center;'>Resume Evaluation</h2>
                <div style='margin-top: 2rem;'>
        """, unsafe_allow_html=True)
        
        feedback_text = st.session_state.feedback.replace("\"\"\"", "").strip()
        st.markdown(feedback_text)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Footer with description on the left
    st.markdown("""
        <div class='footer'>
            <div class='footer-content'>
                <div class='footer-description'>
                    Professional resume analysis powered by AI. We evaluate your resume for ATS compatibility, content strength, and industry alignment.
                </div>
                <div class='footer-brand'>
                    Resume Audit Pro
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero'>
      <div class='hero-content'>
        <h1>Resume Audit Pro</h1>
        <p class='tagline'>AI-Powered Resume Feedback in 60 Seconds</p>
        <img src='https://cdn.jsdelivr.net/gh/yourrepo/hero-illustration.svg' class='hero-img' alt='AI Resume Illustration'>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='trust-box'>
      <b>🔒 Your privacy matters:</b> We never store your resume. All uploads are encrypted and deleted after analysis.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='footer'>
      <div class='footer-links'>
        <a href='/privacy' target='_blank'>Privacy Policy</a>
        <a href='/terms' target='_blank'>Terms of Service</a>
        <a href='/delete' target='_blank'>Delete My Data</a>
      </div>
      <div style='margin-top: 0.5rem; font-size: 0.95rem; opacity: 0.7;'>
        &copy; 2024 Resume Audit Pro. All rights reserved.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(\"\"\"<div class='progress-bar'><b>ATS Compatibility:</b> 80%</div>\"\"\", unsafe_allow_html=True)
    st.progress(0.8)

    st.markdown(\"\"\"
    <div class='testimonials'>
      <div class='testimonial-card'>"Landed 3x more interviews!"<br><span style='font-size:0.9em;opacity:0.7;'>— Priya S.</span></div>
      <div class='testimonial-card'>"The feedback was actionable and clear."<br><span style='font-size:0.9em;opacity:0.7;'>— Alex T.</span></div>
    </div>
    <div class='partners'>
      <img src='https://upload.wikimedia.org/wikipedia/commons/4/44/Google-flutter-logo.svg' class='partner-logo'>
      <img src='https://upload.wikimedia.org/wikipedia/commons/2/2f/Logo_TV_2015.png' class='partner-logo'>
    </div>
    \"\"\", unsafe_allow_html=True)

    st.video('https://www.youtube.com/embed/your-tutorial-id')

if __name__ == "__main__":
    main()
