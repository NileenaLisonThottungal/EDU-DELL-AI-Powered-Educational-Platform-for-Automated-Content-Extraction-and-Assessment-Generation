from modules.quiz_grading import grade_quiz
from modules.storage import get_attempt, get_quiz, list_attempts_for_session, save_attempt, save_quiz


def _sample_quiz():
    questions = [
        {"id": 1, "question": "What enables scaling?", "options": ["Replication", "Deletion", "Caching", "Sorting"],
         "correct_answer": "Replication", "explanation": "Replication enables scaling."},
        {"id": 2, "question": "____ stores embeddings.", "correct_answer": "ChromaDB",
         "explanation": "ChromaDB stores embeddings."},
    ]
    return save_quiz("doc-1", "mcq", questions, difficulty="medium")


def test_save_and_get_quiz_round_trips():
    quiz = _sample_quiz()
    fetched = get_quiz(quiz["id"])
    assert fetched["quiz_type"] == "mcq"
    assert len(fetched["questions"]) == 2


def test_grade_quiz_scores_correct_and_incorrect_answers():
    quiz = _sample_quiz()
    score, total, breakdown = grade_quiz(quiz, {"1": "Replication", "2": "wrong answer"})

    assert score == 1
    assert total == 2
    assert breakdown[0]["is_correct"] is True
    assert breakdown[1]["is_correct"] is False


def test_save_attempt_and_list_by_session():
    quiz = _sample_quiz()
    score, total, breakdown = grade_quiz(quiz, {"1": "Replication", "2": "ChromaDB"})
    attempt = save_attempt(quiz["id"], "session-abc", "mcq", score, total, breakdown)

    fetched = get_attempt(attempt["id"])
    assert fetched["score"] == 2

    attempts = list_attempts_for_session("session-abc")
    assert len(attempts) == 1
    assert attempts[0]["id"] == attempt["id"]


def test_list_attempts_for_unknown_session_is_empty():
    assert list_attempts_for_session("no-such-session") == []
