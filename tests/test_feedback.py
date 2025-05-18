from app.feedback import get_resume_feedback

def test_get_resume_feedback_mock(monkeypatch):
    def mock_generate_content(self, prompt):
        class MockResponse:
            text = "Mock feedback generated."
        return MockResponse()

    import google.generativeai as genai
    genai.GenerativeModel.generate_content = mock_generate_content

    result = get_resume_feedback("Sample resume text", "Data Scientist", "fake-key")
    assert "Mock feedback" in result
