import json
import uuid
from datetime import datetime, timezone

from modules.storage.db import get_connection


def save_document(filename: str, raw_text: str, sentences: list[str]) -> dict:
    document_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, raw_text, sentences_json, summary, created_at) "
            "VALUES (?, ?, ?, ?, NULL, ?)",
            (document_id, filename, raw_text, json.dumps(sentences), created_at),
        )

    return {
        "id": document_id,
        "filename": filename,
        "raw_text": raw_text,
        "sentences": sentences,
        "summary": None,
        "created_at": created_at,
    }


def get_document(document_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "filename": row["filename"],
        "raw_text": row["raw_text"],
        "sentences": json.loads(row["sentences_json"]),
        "summary": row["summary"],
        "created_at": row["created_at"],
    }


def list_documents() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, summary, created_at FROM documents ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def save_summary(document_id: str, summary: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE documents SET summary = ? WHERE id = ?", (summary, document_id))
