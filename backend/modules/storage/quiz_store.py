import json
import uuid
from datetime import datetime, timezone

from modules.storage.db import get_connection


def save_quiz(document_id: str, quiz_type: str, questions: list[dict], difficulty: str | None = None) -> dict:
    quiz_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO quizzes (id, document_id, quiz_type, difficulty, questions_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (quiz_id, document_id, quiz_type, difficulty, json.dumps(questions), created_at),
        )

    return {
        "id": quiz_id,
        "document_id": document_id,
        "quiz_type": quiz_type,
        "difficulty": difficulty,
        "questions": questions,
        "created_at": created_at,
    }


def get_quiz(quiz_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "document_id": row["document_id"],
        "quiz_type": row["quiz_type"],
        "difficulty": row["difficulty"],
        "questions": json.loads(row["questions_json"]),
        "created_at": row["created_at"],
    }
