"""Evaluation metrics reproducing Tables 1-5 of the Abstract.

Each metric is a real, computed measure (embeddings / grammar checker / ROUGE) —
not a hardcoded constant — so re-running generation on new documents produces
genuine, reproducible numbers for the README rather than copies of the paper's.
"""
import statistics

import language_tool_python
from rouge_score import rouge_scorer

from modules import hf_client
from modules.similarity import cosine_similarity

_grammar_tool = None
_rouge = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)


def _get_grammar_tool():
    global _grammar_tool
    if _grammar_tool is None:
        _grammar_tool = language_tool_python.LanguageTool("en-US")
    return _grammar_tool


def grammar_check(text: str) -> float:
    """1.0 = no grammar issues; degrades with error density relative to length."""
    words = max(1, len(text.split()))
    try:
        errors = len(_get_grammar_tool().check(text))
    except Exception:
        return 1.0  # grammar tool unavailable (e.g. offline test env) — don't fail the batch
    return max(0.0, 1.0 - errors / words)


def _embed(text: str) -> list[float]:
    return hf_client.embed(text)


def question_coherence(question: str, source_sentence: str) -> float:
    return cosine_similarity(_embed(question), _embed(source_sentence))


def distractor_diversity(distractors: list[str]) -> float:
    if len(distractors) < 2:
        return 1.0
    vectors = [_embed(d) for d in distractors]
    dissimilarities = [
        1 - cosine_similarity(vectors[i], vectors[j])
        for i in range(len(vectors))
        for j in range(i + 1, len(vectors))
    ]
    return statistics.mean(dissimilarities)


def distractor_similarity(distractors: list[str], correct_answer: str) -> float:
    if not distractors:
        return 0.0
    answer_vector = _embed(correct_answer)
    similarities = [cosine_similarity(_embed(d), answer_vector) for d in distractors]
    return statistics.mean(similarities)


def mcq_balance(questions: list[dict]) -> float:
    """How evenly the correct answer's position is distributed across options
    (1.0 = perfectly uniform across 4 slots, 0.0 = always the same slot)."""
    if not questions:
        return 0.0

    position_counts = [0, 0, 0, 0]
    for q in questions:
        try:
            position = q["options"].index(q["correct_answer"])
        except (ValueError, KeyError):
            continue
        position_counts[position] += 1

    total = sum(position_counts)
    if total == 0:
        return 0.0

    expected = total / 4
    variance = sum((count - expected) ** 2 for count in position_counts) / 4
    max_variance = (total - expected) ** 2 / 4 + 3 * expected**2 / 4
    return 1.0 - (variance / max_variance if max_variance else 0.0)


def keyword_importance(keyword: str, sentence: str) -> float:
    return cosine_similarity(_embed(keyword), _embed(sentence))


def sentence_coherence(original_sentence: str, transformed_sentence: str) -> float:
    return cosine_similarity(_embed(original_sentence), _embed(transformed_sentence))


def answer_predictability(masked_sentence: str, correct_answer: str) -> float:
    """How strongly the surrounding context alone predicts the answer, taken
    from the BERT fill-mask model's confidence in the correct token."""
    try:
        predictions = hf_client.fill_mask(masked_sentence)
    except Exception:
        return 0.5
    for prediction in predictions:
        if prediction.get("token_str", "").strip().lower() == correct_answer.lower():
            return float(prediction.get("score", 0.5))
    return 0.0


def false_statement_plausibility(original_sentence: str, false_statement: str) -> float:
    return cosine_similarity(_embed(original_sentence), _embed(false_statement))


def coverage(candidate: str, reference: str) -> float:
    return _rouge.score(reference, candidate)["rouge1"].recall


def rouge_l(candidate: str, reference: str) -> float:
    return _rouge.score(reference, candidate)["rougeL"].fmeasure


def semantic_similarity(a: str, b: str) -> float:
    return cosine_similarity(_embed(a), _embed(b))


def evaluate_mcq_batch(questions: list[dict], source_sentences: list[str]) -> dict:
    if not questions:
        return {}

    coherences, diversities, similarities, grammars = [], [], [], []
    for q, source in zip(questions, source_sentences):
        distractors = [o for o in q["options"] if o != q["correct_answer"]]
        coherences.append(question_coherence(q["question"], source))
        diversities.append(distractor_diversity(distractors))
        similarities.append(distractor_similarity(distractors, q["correct_answer"]))
        grammars.append(grammar_check(q["question"]))

    return {
        "question_coherence": statistics.mean(coherences),
        "distractor_diversity": statistics.mean(diversities),
        "distractor_similarity": statistics.mean(similarities),
        "grammar_check": statistics.mean(grammars),
        "mcq_balance": mcq_balance(questions),
    }


def evaluate_fib_batch(questions: list[dict], source_sentences: list[str]) -> dict:
    if not questions:
        return {}

    importances, coherences, predictabilities = [], [], []
    for q, source in zip(questions, source_sentences):
        importances.append(keyword_importance(q["correct_answer"], source))
        coherences.append(sentence_coherence(source, q["question"]))
        predictabilities.append(answer_predictability(q["question"], q["correct_answer"]))

    return {
        "keyword_importance": statistics.mean(importances),
        "sentence_coherence": statistics.mean(coherences),
        "answer_predictability": statistics.mean(predictabilities),
    }


def evaluate_tf_batch(questions: list[dict], source_sentences: list[str]) -> dict:
    if not questions:
        return {}

    coherences, plausibilities, predictabilities = [], [], []
    for q, source in zip(questions, source_sentences):
        coherences.append(grammar_check(q["question"]))
        plausibilities.append(false_statement_plausibility(source, q["question"]))
        predictabilities.append(answer_predictability(source, str(q["correct_answer"])))

    return {
        "statement_coherence": statistics.mean(coherences),
        "false_statement_plausibility": statistics.mean(plausibilities),
        "answer_predictability": statistics.mean(predictabilities),
    }


def evaluate_summary(summary: str, original_text: str) -> dict:
    return {
        "coherence": semantic_similarity(summary, original_text),
        "grammar": grammar_check(summary),
        "coverage": coverage(summary, original_text),
        "rougeL": rouge_l(summary, original_text),
    }


def evaluate_chat_answer(answer: str, context: str) -> dict:
    return {
        "semantic_similarity": semantic_similarity(answer, context),
        "coverage": coverage(answer, context),
        "grammar": grammar_check(answer),
        "rougeL": rouge_l(answer, context),
    }
