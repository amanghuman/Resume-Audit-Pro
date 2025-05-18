import streamlit as st

def apply_custom_css():
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
