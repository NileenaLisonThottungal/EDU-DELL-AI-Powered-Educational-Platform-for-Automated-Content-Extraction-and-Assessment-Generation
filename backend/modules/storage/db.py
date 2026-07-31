"""SQLite persistence: uploaded documents, generated quizzes, and quiz attempts
(score history). One small file-backed DB — no auth, sessions are just a
client-generated id stored in localStorage (Section 11 of doc.md: extras)."""
import sqlite3
from contextlib import contextmanager

from config import Config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    sentences_json TEXT NOT NULL,
    summary TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quizzes (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    quiz_type TEXT NOT NULL,
    difficulty TEXT,
    questions_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents (id)
);

CREATE TABLE IF NOT EXISTS attempts (
    id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    quiz_type TEXT NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    breakdown_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
);
"""


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(_SCHEMA)


@contextmanager
def get_connection():
    conn = sqlite3.connect(Config.ATTEMPTS_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
