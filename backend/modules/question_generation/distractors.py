"""Distractor generation: BERT masked-word prediction + WordNet synonyms,
filtered by Sentence-BERT similarity (Algorithm 1, Section 4 difficulty extension).

Difficulty controls how close the distractors are allowed to be to the correct
answer, by cosine-similarity band against the keyword's embedding:
  - easy:   similarity in [0.0, 0.35)  -> obviously-wrong options
  - medium: similarity in [0.20, 0.60) -> plausible but distinguishable
  - hard:   similarity in [0.45, 0.85) -> close, tricky options
Bands overlap slightly and are relaxed automatically if too few candidates match,
so a valid MCQ can always be formed even for short/unusual keywords.
"""
import re

from nltk.corpus import wordnet

from modules import hf_client
from modules.similarity import cosine_similarity

_DIFFICULTY_BANDS = {
    "easy": (0.0, 0.35),
    "medium": (0.20, 0.60),
    "hard": (0.45, 0.85),
}
_WORD_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\-]*$")


def _wordnet_synonyms(keyword: str) -> list[str]:
    synonyms = set()
    for synset in wordnet.synsets(keyword):
        for lemma in synset.lemmas():
            candidate = lemma.name().replace("_", " ")
            if candidate.lower() != keyword.lower():
                synonyms.add(candidate)
    return list(synonyms)


def _bert_mask_candidates(sentence: str, keyword: str, top_k: int = 15) -> list[str]:
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    if not pattern.search(sentence):
        return []

    masked_sentence = pattern.sub(hf_client.BERT_MASK_TOKEN, sentence, count=1)
    try:
        predictions = hf_client.fill_mask(masked_sentence, top_k=top_k)
    except Exception:
        return []

    candidates = []
    for prediction in predictions:
        token = prediction.get("token_str", "").strip()
        if token and token.lower() != keyword.lower() and _WORD_PATTERN.match(token):
            candidates.append(token)
    return candidates


def generate_distractors(
    sentence: str, keyword: str, num_distractors: int = 3, difficulty: str = "medium"
) -> list[str]:
    candidates = list(dict.fromkeys(_bert_mask_candidates(sentence, keyword) + _wordnet_synonyms(keyword)))
    if not candidates:
        return []

    try:
        keyword_vector = hf_client.embed(keyword)
        candidate_vectors = hf_client.embed(candidates)
    except Exception:
        # Embedding service unavailable: fall back to unfiltered candidates.
        return candidates[:num_distractors]

    scored = [
        (candidate, cosine_similarity(keyword_vector, vector))
        for candidate, vector in zip(candidates, candidate_vectors)
    ]

    band = _DIFFICULTY_BANDS.get(difficulty, _DIFFICULTY_BANDS["medium"])
    selected = _select_by_band(scored, band, num_distractors)

    # Relax progressively if the band was too narrow for this keyword.
    relaxation = 0.1
    while len(selected) < num_distractors and (band[0] - relaxation) > -1:
        relaxed_band = (max(0.0, band[0] - relaxation), min(1.0, band[1] + relaxation))
        selected = _select_by_band(scored, relaxed_band, num_distractors)
        relaxation += 0.1

    return [candidate for candidate, _ in selected][:num_distractors]


def _select_by_band(scored: list[tuple], band: tuple, count: int) -> list[tuple]:
    in_band = [item for item in scored if band[0] <= item[1] <= band[1]]
    in_band.sort(key=lambda item: item[1], reverse=True)

    if len(in_band) >= count:
        return _diversify(in_band, count)

    remaining = [item for item in scored if item not in in_band]
    remaining.sort(key=lambda item: abs(item[1] - sum(band) / 2))
    return _diversify(in_band + remaining, count)


def _diversify(scored: list[tuple], count: int) -> list[tuple]:
    """Greedily pick candidates that are dissimilar from each other, not just
    from the keyword, to maximize the Distractor Diversity metric (Table 1)."""
    if len(scored) <= count:
        return scored

    selected = [scored[0]]
    remaining = scored[1:]

    while len(selected) < count and remaining:
        remaining.sort(
            key=lambda item: min(abs(item[1] - chosen[1]) for chosen in selected),
            reverse=True,
        )
        selected.append(remaining.pop(0))

    return selected
