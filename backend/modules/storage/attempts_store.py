import json
import uuid
from datetime import datetime, timezone

from modules.storage.db import get_connection


def save_attempt(quiz_id: str, session_id: str, quiz_type: str, score: int, total: int, breakdown: list[dict]) -> dict:
    attempt_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO attempts (id, quiz_id, session_id, quiz_type, score, total, breakdown_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (attempt_id, quiz_id, session_id, quiz_type, score, total, json.dumps(breakdown), created_at),
        )

    return {
        "id": attempt_id,
        "quiz_id": quiz_id,
        "session_id": session_id,
        "quiz_type": quiz_type,
        "score": score,
        "total": total,
        "breakdown": breakdown,
        "created_at": created_at,
    }


def get_attempt(attempt_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()

    if row is None:
        return None

    return _row_to_dict(row)


def list_attempts_for_session(session_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM attempts WHERE session_id = ? ORDER BY created_at ASC", (session_id,)
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "quiz_id": row["quiz_id"],
        "session_id": row["session_id"],
        "quiz_type": row["quiz_type"],
        "score": row["score"],
        "total": row["total"],
        "breakdown": json.loads(row["breakdown_json"]),
        "created_at": row["created_at"],
    }
