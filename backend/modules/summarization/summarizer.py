"""Gemini-powered summarization (Section 3.1.5 / 3.5)."""
from modules import gemini_client

_SUMMARY_PROMPT = (
    "Summarize the following educational document in 4-6 concise, clear sentences "
    "suitable for a student revising the material. Focus on the key concepts.\n\n"
    "Document:\n{text}"
)
_MAX_INPUT_CHARS = 20000


def summarize_document(text: str) -> str:
    truncated = text[:_MAX_INPUT_CHARS]
    prompt = _SUMMARY_PROMPT.format(text=truncated)
    return gemini_client.generate(prompt)
