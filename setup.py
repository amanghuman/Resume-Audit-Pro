from setuptools import setup, find_packages

setup(
    name="resume_audit_pro",
    version="0.1.0",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[
        "streamlit",
        "pdfplumber",
        "python-dotenv",
        "google-generativeai"
    ],
    entry_points={
        'console_scripts': [
            'resume-audit=app.main:main'
        ]
    },
)
