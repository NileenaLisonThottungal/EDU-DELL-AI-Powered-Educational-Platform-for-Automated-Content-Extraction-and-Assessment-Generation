"""Scores a submitted quiz attempt against its stored correct answers."""


def _normalize(value) -> str:
    return str(value).strip().lower()


def grade_quiz(quiz: dict, submitted_answers: dict) -> tuple[int, int, list[dict]]:
    """submitted_answers maps question id (as string) -> the user's answer."""
    breakdown = []
    score = 0

    for question in quiz["questions"]:
        question_id = str(question["id"])
        submitted = submitted_answers.get(question_id)
        correct = question["correct_answer"]

        is_correct = submitted is not None and _normalize(submitted) == _normalize(correct)
        if is_correct:
            score += 1

        breakdown.append(
            {
                "question_id": question["id"],
                "question": question["question"],
                "submitted_answer": submitted,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
            }
        )

    return score, len(quiz["questions"]), breakdown
