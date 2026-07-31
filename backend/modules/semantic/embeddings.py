"""Sentence-BERT embeddings via the Hugging Face Inference API (Section 3.4)."""
from modules import hf_client


def embed_text(text: str) -> list[float]:
    return hf_client.embed(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return hf_client.embed(texts)
