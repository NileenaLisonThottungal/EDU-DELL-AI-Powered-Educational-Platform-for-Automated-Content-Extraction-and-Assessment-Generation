"""Algorithm 3: True or False Generation from Text.

Pure spaCy/WordNet pipeline (no LLM calls), per the Abstract's Table 1.
"""
import random
import re

from nltk.corpus import wordnet

from modules.question_generation.keyword_extractor import pick_primary_keyword

_GENERIC_INCORRECT_TERMS = ("process", "value", "system", "structure", "method")


def _wordnet_antonym(keyword: str) -> str | None:
    for synset in wordnet.synsets(keyword):
        for lemma in synset.lemmas():
            for antonym in lemma.antonyms():
                candidate = antonym.name().replace("_", " ")
                if candidate.lower() != keyword.lower():
                    return candidate
    return None


def _falsify(sentence: str, keyword: str) -> str:
    replacement = _wordnet_antonym(keyword)
    if replacement is None:
        replacement = random.choice([t for t in _GENERIC_INCORRECT_TERMS if t != keyword.lower()])

    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(replacement, sentence, count=1)


def generate_tf_questions(sentences: list[str], num_questions: int = 5) -> list[dict]:
    candidates = list(sentences)
    random.shuffle(candidates)

    questions = []
    for sentence in candidates:
        if len(questions) >= num_questions:
            break

        keyword = pick_primary_keyword(sentence)
        if not keyword:
            continue

        is_true = random.choice([True, False])
        statement = sentence if is_true else _falsify(sentence, keyword)

        questions.append(
            {
                "id": len(questions) + 1,
                "question": statement,
                "correct_answer": is_true,
                "explanation": f"The original text states: \"{sentence}\"",
            }
        )

    return questions
