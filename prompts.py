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
