from .cleaner import clean_text
from .segmenter import segment_into_sentences


def preprocess(raw_text: str) -> list[str]:
    """Full pipeline: clean noisy text, then segment into a filtered sentence pool."""
    return segment_into_sentences(clean_text(raw_text))


__all__ = ["clean_text", "segment_into_sentences", "preprocess"]
