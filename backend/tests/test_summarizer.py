from modules.summarization import summarize_document
from tests.conftest import SAMPLE_TEXT


def test_summarize_document_returns_mocked_gemini_response():
    summary = summarize_document(SAMPLE_TEXT)
    assert summary
    assert "mocked Gemini response" in summary
