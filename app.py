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
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Space+Grotesk:wght@400;500;600&display=swap');

        /* Base styles */
        :root {
            --bg-color: #222831;
            --secondary-dark: #393E46;
            --accent: #00ADB5;
            --text-color: #EEEEEE;
            --border-color: #4A4F57;
            --hover-color: #2C3138;
            --gradient-start: #00ADB5;
            --gradient-end: #006D73;
        }

        /* Global styles */
        .main {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Poppins', sans-serif;
        }
        
        /* Typography */
        h1 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text-color) !important;
            font-size: 2.2rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        h2 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--text-color) !important;
            font-size: 1.5rem !important;
            font-weight: 500 !important;
            margin: 0 !important;
            letter-spacing: -0.3px;
        }
        
        p {
            color: var(--text-color);
            font-size: 1rem !important;
            line-height: 1.6 !important;
            margin: 0.75rem 0 !important;
            opacity: 0.9;
        }

        /* Containers */
        .info-box {
            background-color: var(--secondary-dark);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .feedback-section {
            background-color: var(--secondary-dark);
            padding: 1.8rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s ease;
        }

        .feedback-section:hover {
            transform: translateY(-2px);
        }

        /* File uploader */
        .stFileUploader {
            background-color: var(--secondary-dark) !important;
        }
        
        .css-1upf2ak {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            padding: 1.8rem !important;
            transition: border-color 0.2s ease !important;
        }

        .css-1upf2ak:hover {
            border-color: var(--accent) !important;
        }

        /* Buttons */
        .stButton button {
            font-family: 'Space Grotesk', sans-serif !important;
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
            color: var(--text-color) !important;
            font-weight: 500 !important;
            padding: 0.9rem 2rem !important;
            border-radius: 8px !important;
            border: none !important;
            transition: all 0.2s ease !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stButton button:hover {
            opacity: 0.9 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0, 173, 181, 0.2) !important;
        }

        /* Input fields */
        .stTextInput input {
            font-family: 'Poppins', sans-serif !important;
            background-color: var(--secondary-dark) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: var(--text-color) !important;
            border-radius: 8px !important;
            padding: 0.9rem 1.2rem !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stTextInput input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(0, 173, 181, 0.1) !important;
            transform: translateY(-1px);
        }

        /* Messages */
        .success-box, .warning-box {
            background-color: var(--secondary-dark);
            padding: 1.2rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-size: 0.95rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .success-box {
            border-left: 3px solid var(--accent);
        }
        
        .warning-box {
            border-left: 3px solid #FFA726;
        }

        /* Footer */
        .footer {
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border-color);
        }

        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .footer-description {
            font-size: 0.9rem;
            color: var(--text-color);
            opacity: 0.7;
            max-width: 600px;
            text-align: left;
        }

        .footer-brand {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            color: var(--text-color);
            opacity: 0.9;
            font-weight: 500;
        }

        /* Spinner */
        .stSpinner > div {
            border-color: var(--accent) !important;
            border-right-color: transparent !important;
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
            background: var(--secondary-dark);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent);
        }

        /* Placeholder text */
        ::placeholder {
            color: rgba(238, 238, 238, 0.5) !important;
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

if __name__ == "__main__":
    main()
