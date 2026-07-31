from modules.preprocessing import preprocess
from modules.question_generation.fib_generator import generate_fib_questions
from tests.conftest import SAMPLE_TEXT


def test_generate_fib_questions_blanks_a_keyword():
    sentences = preprocess(SAMPLE_TEXT)
    questions = generate_fib_questions(sentences, num_questions=3)

    assert 1 <= len(questions) <= 3
    for question in questions:
        assert "____" in question["question"]
        assert question["correct_answer"]
        assert question["explanation"]


def test_generate_fib_questions_handles_empty_input():
    assert generate_fib_questions([], num_questions=5) == []
