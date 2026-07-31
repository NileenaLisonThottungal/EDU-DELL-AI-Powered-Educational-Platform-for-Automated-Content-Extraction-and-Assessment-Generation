"""Algorithm 2: Fill-in-the-Blanks Generation from Text.

Pure spaCy/rule-based pipeline (no LLM calls) per the Abstract's Table 1
("Fill-in-the-Blank ... does not involve large language models").
"""
import random
import re

from modules.question_generation.keyword_extractor import pick_primary_keyword

_BLANK = "____"


def _blank_first_occurrence(sentence: str, keyword: str) -> str:
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(_BLANK, sentence, count=1)


def generate_fib_questions(sentences: list[str], num_questions: int = 5) -> list[dict]:
    candidates = list(sentences)
    random.shuffle(candidates)

    questions = []
    for sentence in candidates:
        if len(questions) >= num_questions:
            break

        keyword = pick_primary_keyword(sentence)
        if not keyword:
            continue

        blanked_sentence = _blank_first_occurrence(sentence, keyword)
        if _BLANK not in blanked_sentence:
            continue

        questions.append(
            {
                "id": len(questions) + 1,
                "question": blanked_sentence,
                "correct_answer": keyword,
                "explanation": f"The original text states: \"{sentence}\"",
            }
        )

    return questions
