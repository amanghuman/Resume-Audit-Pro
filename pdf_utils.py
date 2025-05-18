# app/pdf_utils.py
import pdfplumber

def extract_text_from_pdf(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip() if text.strip() else None
    except Exception as e:
        return f"PDF Error: {e}"
