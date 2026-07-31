"""Sentence segmentation + filtering rules (Section 3.2.2 / 3.2.3)."""
import re

from modules.nlp_pipeline import get_nlp

_MIN_SENTENCE_LENGTH = 50
_MAX_PUNCTUATION_MARKS = 3
_PUNCTUATION_PATTERN = re.compile(r"[:;]")


def _has_strong_pedagogical_content(sentence: str) -> bool:
    """Short sentences survive filtering if they contain a defining/technical cue."""
    cues = (" is ", " are ", " means ", " refers to ", " defined as ", " enables ")
    lowered = f" {sentence.lower()} "
    return any(cue in lowered for cue in cues)


def segment_into_sentences(cleaned_text: str) -> list[str]:
    doc = get_nlp()(cleaned_text)
    sentences = []

    for sent in doc.sents:
        text = sent.text.strip()
        if not text:
            continue

        if len(text) < _MIN_SENTENCE_LENGTH and not _has_strong_pedagogical_content(text):
            continue

        if len(_PUNCTUATION_PATTERN.findall(text)) > _MAX_PUNCTUATION_MARKS:
            continue

        sentences.append(text)

    return sentences
