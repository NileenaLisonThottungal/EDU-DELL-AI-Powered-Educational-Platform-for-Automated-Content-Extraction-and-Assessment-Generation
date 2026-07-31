"""Algorithm 1: MCQ Generation from Text.

Pipeline (per sentence in the cleaned sentence pool):
  keyword extraction -> distractor generation (BERT + WordNet, Sentence-BERT
  filtered) -> question formation (LLM rewrite of the sentence into a
  question) -> answer shuffling -> validation.
"""
import random

from modules import hf_client
from modules.question_generation.distractors import generate_distractors
from modules.question_generation.keyword_extractor import pick_primary_keyword

_QUESTION_PROMPT = (
    "Rewrite the following sentence as a single, short quiz question that asks "
    "the reader to identify '{keyword}'. Reply with ONLY the question itself, "
    "no options, no explanation. Sentence: {sentence}"
)


def _form_question(sentence: str, keyword: str) -> str:
    prompt = _QUESTION_PROMPT.format(keyword=keyword, sentence=sentence)
    try:
        raw = hf_client.generate_text(prompt, max_new_tokens=48)
    except Exception:
        raw = ""

    question = _extract_question_line(raw)
    if question:
        return question

    # LLM unavailable or produced no usable question: fall back to a
    # deterministic blank-the-keyword transformation so generation never fails.
    return _blank_keyword(sentence, keyword) + "?"


def _extract_question_line(raw: str) -> str | None:
    for line in raw.strip().splitlines():
        line = line.strip().lstrip("*-#>0123456789. ").strip()
        if line.endswith("?"):
            return line
    return None


def _blank_keyword(sentence: str, keyword: str) -> str:
    return sentence.replace(keyword, "____", 1)


def generate_mcqs(sentences: list[str], num_questions: int = 5, difficulty: str = "medium") -> list[dict]:
    candidates = list(sentences)
    random.shuffle(candidates)

    questions = []
    for sentence in candidates:
        if len(questions) >= num_questions:
            break

        keyword = pick_primary_keyword(sentence)
        if not keyword:
            continue

        distractors = generate_distractors(sentence, keyword, num_distractors=3, difficulty=difficulty)
        if len(distractors) < 3:
            continue

        options = distractors[:3] + [keyword]
        random.shuffle(options)

        question_text = _form_question(sentence, keyword)

        questions.append(
            {
                "id": len(questions) + 1,
                "question": question_text,
                "options": options,
                "correct_answer": keyword,
                "explanation": f"The original text states: \"{sentence}\"",
                "difficulty": difficulty,
            }
        )

    return questions
