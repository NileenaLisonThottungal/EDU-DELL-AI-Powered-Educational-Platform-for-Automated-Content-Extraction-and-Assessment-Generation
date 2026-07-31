"""HTML-template -> PDF export for quizzes and results (Section 11 extras).

Uses xhtml2pdf (pure Python, reportlab-backed) rather than WeasyPrint: WeasyPrint
requires the native GTK/Pango/Cairo runtime, which isn't available on a stock
Windows install and would require a separate system-wide installer.
"""
import os
from io import BytesIO

from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
_env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR))

_QUIZ_TYPE_LABELS = {"mcq": "Multiple Choice", "fib": "Fill in the Blanks", "tf": "True or False"}


def _render_pdf(html: str) -> bytes:
    buffer = BytesIO()
    result = pisa.CreatePDF(src=html, dest=buffer)
    if result.err:
        raise RuntimeError("Failed to render PDF from HTML template.")
    return buffer.getvalue()


def export_quiz_pdf(quiz: dict) -> bytes:
    template = _env.get_template("quiz.html")
    html = template.render(
        quiz_type_label=_QUIZ_TYPE_LABELS.get(quiz["quiz_type"], quiz["quiz_type"]),
        question_count=len(quiz["questions"]),
        difficulty=quiz.get("difficulty"),
        questions=quiz["questions"],
    )
    return _render_pdf(html)


def export_results_pdf(quiz: dict, attempt: dict) -> bytes:
    template = _env.get_template("results.html")
    percentage = round((attempt["score"] / attempt["total"]) * 100) if attempt["total"] else 0
    html = template.render(
        quiz_type_label=_QUIZ_TYPE_LABELS.get(quiz["quiz_type"], quiz["quiz_type"]),
        score=attempt["score"],
        total=attempt["total"],
        percentage=percentage,
        breakdown=attempt["breakdown"],
    )
    return _render_pdf(html)
