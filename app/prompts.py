def get_resume_feedback_prompt(resume_text, job_field):
    return f"""
# 📄 Professional Resume Analysis for {job_field} Position

Here is a resume submitted for a {job_field} role. Please evaluate it thoroughly and provide structured feedback in the following format:

1. **Summary**: A concise summary of your overall impression.
2. **Strengths**: Bullet points highlighting the key strengths.
3. **Areas for Improvement**: Bullet points on where the resume could be improved.
4. **ATS Optimization Tips**: Suggestions to improve compatibility with Applicant Tracking Systems.
5. **Grammar & Formatting**: List any grammar, punctuation, or formatting issues.
6. **Overall Rating**: Score the resume from 1 to 10.

Resume to analyze:
"""
{resume_text[:100_000]}
"""

"""
