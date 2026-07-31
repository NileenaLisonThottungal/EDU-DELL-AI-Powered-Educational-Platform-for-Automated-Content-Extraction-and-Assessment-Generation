from modules.preprocessing import preprocess
from modules.question_generation.tf_generator import generate_tf_questions
from tests.conftest import SAMPLE_TEXT


def test_generate_tf_questions_returns_boolean_answers():
    sentences = preprocess(SAMPLE_TEXT)
    questions = generate_tf_questions(sentences, num_questions=4)

    assert 1 <= len(questions) <= 4
    for question in questions:
        assert isinstance(question["correct_answer"], bool)
        assert question["question"]
        assert question["explanation"]


def test_generate_tf_questions_handles_empty_input():
    assert generate_tf_questions([], num_questions=5) == []
