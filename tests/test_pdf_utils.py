from app.pdf_utils import extract_text_from_pdf

def test_extract_text_from_pdf_valid(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
    result = extract_text_from_pdf(str(pdf_path))
    assert isinstance(result, str) or result is None
