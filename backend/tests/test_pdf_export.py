from modules.export.pdf_export import export_quiz_pdf, export_results_pdf
from modules.quiz_grading import grade_quiz
from modules.storage import save_attempt, save_quiz


def _sample_quiz():
    questions = [
        {"id": 1, "question": "What enables scaling?", "options": ["Replication", "Deletion", "Caching", "Sorting"],
         "correct_answer": "Replication", "explanation": "Replication enables scaling."},
    ]
    return save_quiz("doc-1", "mcq", questions, difficulty="medium")


def test_export_quiz_pdf_produces_valid_pdf_bytes():
    quiz = _sample_quiz()
    pdf_bytes = export_quiz_pdf(quiz)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100


def test_export_results_pdf_produces_valid_pdf_bytes():
    quiz = _sample_quiz()
    score, total, breakdown = grade_quiz(quiz, {"1": "Replication"})
    attempt = save_attempt(quiz["id"], "session-1", "mcq", score, total, breakdown)

    pdf_bytes = export_results_pdf(quiz, attempt)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 100
