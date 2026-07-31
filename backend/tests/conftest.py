"""Shared pytest fixtures. All Hugging Face Inference API and Gemini calls are
mocked here so the entire suite runs green with no network access and no API
keys — see doc.md Section 9."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config  # noqa: E402
from modules import gemini_client, hf_client  # noqa: E402

_FAKE_MASK_WORDS = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa"]


def _fake_embed(texts, model=None):
    def vector_for(text: str) -> list[float]:
        return [((sum(ord(c) for c in text) * (i + 7)) % 97) / 97.0 for i in range(1, 17)]

    if isinstance(texts, str):
        return vector_for(texts)
    return [vector_for(t) for t in texts]


def _fake_generate_text(prompt, max_new_tokens=64, model=None):
    return "What key concept does this describe?"


def _fake_fill_mask(text_with_mask, model=None, top_k=10):
    return [
        {"token_str": word, "score": round(1.0 - i * 0.05, 3)}
        for i, word in enumerate(_FAKE_MASK_WORDS[:top_k])
    ]


def _fake_gemini_generate(prompt: str) -> str:
    return "This is a mocked Gemini response grounded in the provided context."


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    monkeypatch.setattr(hf_client, "embed", _fake_embed)
    monkeypatch.setattr(hf_client, "generate_text", _fake_generate_text)
    monkeypatch.setattr(hf_client, "fill_mask", _fake_fill_mask)
    monkeypatch.setattr(gemini_client, "generate", _fake_gemini_generate)


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "ATTEMPTS_DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(Config, "CHROMA_DIR", str(tmp_path / "chroma"))

    from modules.semantic import chroma_store
    from modules.storage import db

    monkeypatch.setattr(chroma_store, "_client", None)
    monkeypatch.setattr(chroma_store, "_documents_collection", None)
    monkeypatch.setattr(chroma_store, "_chunks_collection", None)

    db.init_db()


@pytest.fixture
def app(isolated_storage):
    import app as flask_app_module

    flask_app_module.app.testing = True
    return flask_app_module.app


@pytest.fixture
def client(app):
    return app.test_client()


SAMPLE_TEXT = (
    "Consistency in distributed systems means that all nodes observe the same data "
    "at the same time. Replication enables horizontal scaling across many servers. "
    "A vector database stores embeddings and supports fast semantic similarity search. "
    "ChromaDB is a lightweight open source vector database used for retrieval. "
    "Sentence transformers convert text into dense numerical embeddings for comparison."
)
