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
        /* Dark theme colors - New Color Scheme */
        :root {
            /* Base Colors */
            --bg-color: #1A1A1A;
            --secondary-dark: #2D2D2D;
            --text-color: #E0E0E0;
            
            /* Accent Colors */
            --primary-color: #2D8CFF;
            --primary-hover: #66B2FF;
            --teal: #00C1A3;
            --teal-hover: #00E6BF;
            --gold: #FFD700;
            --gold-hover: #FFE44D;
            --error: #FF4D4D;
            --error-hover: #FF6666;
            
            /* Utility Colors */
            --gray: #6B6B6B;
            --success: #4CAF50;
            --warning: #FFA726;
            
            /* Additional UI Colors */
            --card-bg: var(--secondary-dark);
            --border-color: #404040;
            --hover-color: #363636;
        }

        /* Main container */
        .main {
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: var(--gold) !important;
            font-size: 3rem !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
            letter-spacing: 0.5px;
        }
        h2 {
            color: var(--primary-color) !important;
            font-size: 2rem !important;
            font-weight: 600 !important;
            margin-top: 2rem !important;
            letter-spacing: 0.3px;
        }
        h3 {
            color: var(--teal) !important;
            font-size: 1.6rem !important;
            margin-top: 1.5rem !important;
            letter-spacing: 0.2px;
        }
        
        /* Text elements */
        p, li, span {
            color: var(--text-color);
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
            letter-spacing: 0.2px;
        }

        /* Custom containers */
        .info-box {
            background-color: var(--secondary-dark);
            border-left: 5px solid var(--primary-color);
            padding: 1.8rem;
            margin: 1.5rem 0;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        .success-box {
            background-color: rgba(76, 175, 80, 0.1);
            border-left: 5px solid var(--success);
            padding: 1.8rem;
            margin: 1.5rem 0;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        
        .warning-box {
            background-color: rgba(255, 167, 38, 0.1);
            border-left: 5px solid var(--warning);
            padding: 1.8rem;
            margin: 1.5rem 0;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        /* Feature grid */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
            text-align: center;
        }
        
        .feature-item {
            background-color: var(--secondary-dark);
            padding: 1.5rem;
            border-radius: 0.8rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .feature-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            border-color: var(--primary-color);
        }

        /* File uploader */
        .uploadedFile {
            background-color: var(--secondary-dark);
            border: 2px dashed var(--primary-color);
            border-radius: 1rem;
            padding: 2rem;
            margin: 1.5rem 0;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        /* Style for the drag and drop text */
        .css-1upf2ak {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
            border: 2px dashed var(--primary-color) !important;
        }
        
        /* Style for the browse files button */
        .css-1upf2ak:hover {
            border-color: var(--primary-hover) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, var(--primary-color), var(--teal)) !important;
            color: white !important;
            font-weight: 600;
            padding: 1rem 2.5rem;
            border-radius: 0.8rem;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            font-size: 1.1rem !important;
            letter-spacing: 0.5px;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            background: linear-gradient(135deg, var(--primary-hover), var(--teal-hover)) !important;
        }

        /* Input fields */
        .stTextInput input {
            background-color: var(--secondary-dark) !important;
            border: 2px solid var(--border-color) !important;
            color: var(--text-color) !important;
            border-radius: 0.8rem !important;
            padding: 1rem 1.2rem !important;
            font-size: 1.1rem !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(45, 140, 255, 0.2) !important;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 1.5rem 0;
            background-color: var(--secondary-dark);
            border-radius: 1rem;
            overflow: hidden;
        }
        
        th {
            background-color: var(--teal);
            color: var(--text-color);
            padding: 1.2rem;
            text-align: left;
            font-size: 1.1rem;
            letter-spacing: 0.2px;
        }
        
        td {
            padding: 1.2rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-color);
            font-size: 1.1rem;
        }
        
        tr:hover {
            background-color: var(--hover-color);
        }

        /* Feedback section */
        .feedback-section {
            background-color: var(--secondary-dark);
            padding: 2.5rem;
            border-radius: 1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            margin: 2rem 0;
            border: 1px solid var(--border-color);
        }

        /* Footer */
        .footer {
            margin-top: 4rem;
            padding: 2rem 0;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: var(--gray);
        }
        
        .footer-text {
            font-size: 1rem;
            margin-bottom: 1rem;
            color: var(--text-color);
        }

        /* Links */
        a {
            color: var(--primary-color);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        a:hover {
            color: var(--primary-hover);
            text-decoration: underline;
        }

        /* Markdown text */
        .markdown-text-container {
            color: var(--text-color) !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }
        
        /* Code blocks */
        code {
            background-color: var(--hover-color);
            color: var(--primary-color);
            padding: 0.2em 0.4em;
            border-radius: 0.3rem;
            font-size: 0.9em;
        }

        /* Error messages */
        .stAlert {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
            border-left-color: var(--error) !important;
        }

        /* Success messages */
        .stSuccess {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
            border-left-color: var(--success) !important;
        }

        /* Warning messages */
        .stWarning {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
            border-left-color: var(--warning) !important;
        }

        /* File uploader specific styles */
        .stFileUploader {
            background-color: var(--secondary-dark) !important;
        }

        .stFileUploader > div {
            background-color: var(--secondary-dark) !important;
            color: var(--text-color) !important;
        }

        .stFileUploader label {
            color: var(--text-color) !important;
        }

        /* Streamlit default element overrides */
        .stMarkdown {
            color: var(--text-color) !important;
        }

        .element-container {
            color: var(--text-color) !important;
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
