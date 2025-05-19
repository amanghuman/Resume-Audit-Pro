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

if st.button("Run Resume Audit"):
    if not pdf_file or not job_description or not job_field:
        st.error("Please upload a resume, paste a job description, and specify the job field.")
    else:
        # Show spinner while audit is running
        spinner_placeholder.markdown(
            """
            <div style="text-align:center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif" width="50"/>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.spinner("Auditing your resume..."):
            pdf_file.seek(0)  # ✅ FIX 1: Reset file pointer
            with pdfplumber.open(pdf_file) as pdf:
                resume_text = "".join([page.extract_text() or "" for page in pdf.pages])

            if not resume_text.strip():  # ✅ FIX 2: Handle image-based or empty PDFs
                st.error("No extractable text found in the PDF. Please upload a text-based resume.")
                st.stop()

            # Resume Review Prompt for {job_field} Position
            prompt = f"""
Resume Review Prompt for {job_field} Position against {job_description}
You are a **senior hiring manager** with over 20 years of experience at top-tier global companies, specifically in {job_field}.  
Your task is to critically evaluate the resume provided below as if you're deciding whether to shortlist this candidate for a competitive {job_field} role.

Your feedback should be **professional, practical, and tailored for a real-world job search in {job_field}**.  
Focus on **clarity, structure, tone, formatting, keyword alignment**, and **overall impact**—with an eye on how well this resume would perform both with human recruiters and Applicant Tracking Systems (ATS).

---

**Format Required**  
Respond using the *exact* section titles, formatting, and Markdown structure as shown below.  
**Do not skip or add sections. Do not reword headings.**

- **Current Effectiveness (1–10):** 6  
- **Optimized Potential (1–10):** 8  
- **Brief Summary of Strengths & Issues:** Strong technical base, but layout and phrasing limit clarity.  
- **ATS Readiness (Yes/No):** No  
- **Your Key Takeaway (1–2 sentences):** Needs reformatting and stronger action verbs to stand out in ATS and recruiter review.


---

## Major Issues (Red Flags)

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

## ATS Compatibility Check for {job_field}

- **Missing or Weak Keywords:**  
- **Design/Layout Barriers:**  
- **Estimated ATS Score (1–10):**

---

## Fix Recommendations

Below are quick and deep fixes across three key areas of resume improvement: **Content**, **Design**, and **Strategy**.

### Content

**Quick Fix (≤1 hr):**  
- Rewrite bullet points using strong action verbs (e.g., "Led", "Created", "Improved").
- Avoid passive or vague phrases like "Worked on" or "Helped with."
  
**Use this format:**

*[Original bullet from resume]*  

*[Improved version using action verb, clarity, and result]*

**Deep Fix (3–5 hrs):**  
- Reframe each experience to show outcomes and impact. Use the **[Action] + [What you did] + [Result]** format.  
- Add quantifiable metrics (e.g., "increased sales by 15%," "managed budget of $10K").  
- Tailor descriptions to reflect competencies relevant to the target role or industry.

---

### Design

**Quick Fix (≤1 hr):**  
- Use consistent fonts, spacing, and alignment.  
- Make sure section headers are clear and bold, and that margins are not cramped.

**Example (based on resume):**  

*Multiple font sizes used in 'Experience' section*

*Use one consistent font (e.g., Calibri 11pt) and align all bullets to left*

**Deep Fix (3–5 hrs):**  
- Apply a modern, ATS-friendly layout (e.g., left-aligned layout, no columns or graphics).  
- Use section hierarchy (Summary → Skills → Experience → Education → Projects).  
- Remove clutter like icons, photos, or complex visual elements that confuse ATS parsing.

---

### Strategy

**Quick Fix (≤1 hr):**  
- Add 4–6 keywords from a relevant job description (skills, tools, roles).
- Rewrite your summary to clearly state your goal and top strengths.

**Use this format:**

*[Original summary from resume]*  

*[Improved version with clearer career goals and targeted language]*

**Deep Fix (3–5 hrs):**  
- Research 2–3 target job listings and align resume language and structure to match.  
- Prioritize the most relevant experiences—even if not in reverse chronological order.  
- Refine the resume narrative to reflect your career goals and unique value proposition.

---

## Positioning Benchmark for {job_field}

- **Target Level:** (e.g., Internship / Entry-Level / Mid-Level)
- **Resume Tier:** Top 10% / Average / Needs Work
- **One-Line Summary:** (e.g., "Strong foundation, needs polish for ATS and visual clarity.")

---

## Key {job_field} Industry Tips

- Keep it to one page unless you have over 5 years of experience.
- Prioritize results and impact (quantify wherever possible).
- Align language and structure with {job_field} job descriptions.
- Avoid overly designed templates—ATS may not parse them well.
- Proofread for grammar, consistency, and tone.
- Include specific {job_field} technical skills and certifications.

---

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


Job Description:
{job_description}
"""

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)

        # Clear the spinner once complete
        spinner_placeholder.empty()
        st.markdown("## Audit Report")
        st.markdown(response.text)
