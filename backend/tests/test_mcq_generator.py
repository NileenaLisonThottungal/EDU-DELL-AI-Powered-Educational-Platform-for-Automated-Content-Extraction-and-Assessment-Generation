from modules.preprocessing import preprocess
from modules.question_generation.mcq_generator import generate_mcqs
from tests.conftest import SAMPLE_TEXT


def test_generate_mcqs_returns_well_formed_questions():
    sentences = preprocess(SAMPLE_TEXT)
    questions = generate_mcqs(sentences, num_questions=3, difficulty="medium")

    assert 1 <= len(questions) <= 3
    for question in questions:
        assert len(question["options"]) == 4
        assert len(set(question["options"])) == 4  # no duplicate options
        assert question["correct_answer"] in question["options"]
        assert question["question"]
        assert question["explanation"]


def test_generate_mcqs_respects_requested_count():
    sentences = preprocess(SAMPLE_TEXT)
    questions = generate_mcqs(sentences, num_questions=2, difficulty="easy")
    assert len(questions) <= 2


def test_generate_mcqs_handles_empty_input():
    assert generate_mcqs([], num_questions=5) == []
