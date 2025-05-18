import streamlit as st

def render_header():
    st.markdown("<h1>Resume Audit Pro</h1>", unsafe_allow_html=True)

def render_file_upload_section():
    st.subheader("📄 Upload Your Resume")
    return st.file_uploader("PDF only", type="pdf")

def render_job_field_input():
    st.subheader("🎯 Target Role")
    return st.text_input("Enter the job field", placeholder="e.g. Data Scientist")

def render_analyze_button():
    if st.button("Analyze Resume", use_container_width=True):
        st.session_state.analyze_clicked = True

def render_feedback_section(feedback):
    if feedback:
        st.markdown("### ✅ Resume Feedback")
        st.markdown(feedback)

def render_footer():
    st.markdown("---")
    st.markdown("© 2024 Resume Audit Pro | [Privacy](#) | [Terms](#)", unsafe_allow_html=True)
