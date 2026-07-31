"""Shared spaCy pipeline singleton (en_core_web_sm) used across preprocessing
and question generation, so the model is only loaded into memory once."""
import spacy

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp
