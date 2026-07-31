"""Shared Gemini client (google-generativeai), used by summarization and chatbot."""
import google.generativeai as genai

from config import Config

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        _configured = True


def generate(prompt: str) -> str:
    _ensure_configured()
    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    response = model.generate_content(prompt)
    return (response.text or "").strip()
