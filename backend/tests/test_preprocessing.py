from modules.preprocessing.cleaner import clean_text
from modules.preprocessing.segmenter import segment_into_sentences
from tests.conftest import SAMPLE_TEXT


def test_clean_text_removes_bullets_and_noise():
    raw = "•\tIntroduction\n\n\n\nThis is____ a heading----- with noise===="
    cleaned = clean_text(raw)
    assert "•" not in cleaned
    assert "____" not in cleaned
    assert "\t" not in cleaned


def test_clean_text_collapses_blank_lines():
    raw = "line one\n\n\n\n\nline two"
    cleaned = clean_text(raw)
    assert "\n\n\n" not in cleaned


def test_segment_into_sentences_filters_short_fragments():
    sentences = segment_into_sentences("Hi there. " + SAMPLE_TEXT)
    assert "Hi there." not in sentences
    assert any("Consistency" in s for s in sentences)


def test_segment_into_sentences_keeps_short_definitional_sentence():
    sentences = segment_into_sentences("A cache is fast.")
    assert sentences == ["A cache is fast."]


def test_segment_into_sentences_drops_excessive_punctuation():
    noisy = "Section: subsection: item: value: extra: overload for real content here padding text."
    sentences = segment_into_sentences(noisy)
    assert noisy not in sentences
