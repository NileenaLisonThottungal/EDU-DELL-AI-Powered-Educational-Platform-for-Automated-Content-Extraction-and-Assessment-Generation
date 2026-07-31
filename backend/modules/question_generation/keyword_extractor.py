"""Keyword extraction: nouns/proper nouns, stopwords removed (Section 3.3, Algorithms 1-3)."""
from modules.nlp_pipeline import get_nlp

_KEYWORD_POS = ("NOUN", "PROPN")


def extract_keywords(sentence: str) -> list[str]:
    doc = get_nlp()(sentence)
    seen = set()
    keywords = []

    for token in doc:
        if token.pos_ not in _KEYWORD_POS or token.is_stop:
            continue
        lemma = token.text
        if lemma.lower() in seen:
            continue
        seen.add(lemma.lower())
        keywords.append(lemma)

    return keywords


def pick_primary_keyword(sentence: str) -> str | None:
    """Longest keyword tends to be the most content-bearing term to blank out."""
    keywords = extract_keywords(sentence)
    if not keywords:
        return None
    return max(keywords, key=len)
