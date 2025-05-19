import streamlit as st
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
import os
from streamlit_lottie import st_lottie
import requests

# Load environment variables
load_dotenv()
genai.configure(api_key=st.secrets.gemini.api_key)

st.set_page_config(
    page_title="Resume Audit Pro",
    page_icon="",
    layout="wide"
)

# Apply custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_resume = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

col1, col2 = st.columns([6, 1])  # Title and spinner side-by-side

with col1:
    st.markdown("<h1 class='title'>Resume Audit Pro</h1>", unsafe_allow_html=True)

spinner_placeholder = col2.empty()  # Placeholder for black & white spinner

# File upload
st.markdown("## Upload Resume")
pdf_file = st.file_uploader("Upload your resume as a PDF", type=["pdf"])

# Job field input
st.markdown("## Job Field")
job_field = st.text_input("Enter the job field (e.g., Data Science, Marketing, Software Engineering)", max_chars=50)

# Job description input
st.markdown("## Job Description")
job_description = st.text_area("Paste the job description", height=220)

def generate_response(prompt, section_title):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        if not response.text.strip():
            return f"## {section_title}\n\n*No content generated.*"
        return f"## {section_title}\n\n{response.text}"
    except Exception as e:
        return f"## {section_title}\n\n*Error generating this section: {e}*"

if st.button("Run Resume Audit"):
    if not pdf_file or not job_description or not job_field:
        st.error("Please upload a resume, paste a job description, and specify the job field.")
    else:
        spinner_placeholder.markdown(
            """
            <div style="text-align:center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif" width="50"/>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.spinner("Auditing your resume..."):
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                resume_text = "".join([page.extract_text() or "" for page in pdf.pages])

            if not resume_text.strip():
                st.error("No extractable text found in the PDF. Please upload a text-based resume.")
                spinner_placeholder.empty()
                st.stop()

            base_context = f"""
You are a senior hiring manager with over 20 years of experience in {job_field}.  
You're auditing the resume below for a {job_field} role using the job description provided.  

## Response Constraints (Strict)

- **No AI disclaimers** (e.g., "As an AI...", "Good luck...").
- **No filler or vague praise** (e.g., "Great job!", "Looks good.").
- **Stay in character** as a senior hiring manager with 20+ years in {job_field}.
- **Be direct, professional, and role-specific**.
- **All feedback must be specific and actionable** (e.g., include revised bullet points, layout advice, keyword suggestions).
- **Do not explain your process or how you generated the feedback**.
- **Focus only on resume effectiveness, ATS performance, and alignment to {job_field} roles**.

*Final Reminder:*  
Your output will be discarded if it includes:
- AI disclaimers  
- Fluff, encouragement, or "as an AI" language  
- Skipped sections or altered headings

---  
**Resume Text:**  
{resume_text}  

---  
**Job Description:**  
{job_description}  
"""

            # Category-specific prompts
            categories = [
                ("Overall Evaluation", """
Please provide the following overview scores and key points:

- **Current Effectiveness (1–10):**  
- **Optimized Potential (1–10):**  
- **Brief Summary of Strengths & Issues:**  
- **ATS Readiness (Yes/No):**  
- **Your Key Takeaway (1–2 sentences):**  
"""),

                ("Major Issues (Red Flags)", """
Identify critical resume issues using this format:

| Issue | Original Example | Improved Example |
|-------|------------------|------------------|
|       |                  |                  |
Provide actionable and realistic red flags specific to {job_field}.
"""),

                ("ATS Compatibility Check", """
Assess the resume's ATS compatibility. Include:

- **Missing or Weak Keywords:**  
- **Design/Layout Barriers:**  
- **Estimated ATS Score (1–10):**  
"""),

                ("Fix Recommendations", """
Suggest fixes split into **Content**, **Design**, and **Strategy**, with both quick (≤1hr) and deep (3–5hr) improvements in each.
Use examples and rewrite samples as needed.
"""),

                ("Positioning Benchmark", """
Rate the candidate’s level and resume tier. Provide:

- **Target Level:**  
- **Resume Tier:**  
- **One-Line Summary:**  
"""),

                ("Key Industry Tips", f"""
Share 5–7 **{job_field}-specific** resume tips. Avoid general advice.
""")
            ]

            final_output = ""
            for section_title, prompt in categories:
                full_prompt = base_context + prompt
                section_result = generate_response(full_prompt, section_title)
                final_output += section_result + "\n\n---\n\n"

        spinner_placeholder.empty()
        st.markdown("## Audit Report")
        st.markdown(final_output, unsafe_allow_html=True)
