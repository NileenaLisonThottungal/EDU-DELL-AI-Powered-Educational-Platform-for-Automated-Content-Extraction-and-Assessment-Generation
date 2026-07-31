import { useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import Card from "../components/Card.jsx";
import OptionButton from "../components/OptionButton.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import QuestionCard from "../components/QuestionCard.jsx";
import { api } from "../api/client.js";
import { useSessionId } from "../context/SessionContext.jsx";

const TYPE_LABELS = { mcq: "Answer the Questions", fib: "Fill in the Blanks", tf: "True or False" };
const TYPE_ICONS = { mcq: "📖", fib: "📝", tf: "✅" };

export default function QuizPage() {
  const { quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = useSessionId();

  const quiz = location.state?.quiz;
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const answeredCount = useMemo(() => Object.keys(answers).length, [answers]);

  if (!quiz) {
    return (
      <div className="mx-auto max-w-lg px-4 py-10 text-center text-white">
        <p>This quiz session was lost (e.g. after a page refresh).</p>
        <button onClick={() => navigate("/")} className="mt-4 underline">
          Start a new quiz
        </button>
      </div>
    );
  }

  const setAnswer = (questionId, value) => {
    setAnswers((current) => ({ ...current, [String(questionId)]: value }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const attempt = await api.submitQuiz(quizId, answers, sessionId);
      navigate(`/results/${quizId}`, { state: { quiz, attempt } });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex justify-center px-4 py-8">
      <Card className="w-full max-w-xl p-6">
        <h1 className="mb-1 flex items-center gap-2 text-xl font-bold">
          {TYPE_ICONS[quiz.quiz_type]} {TYPE_LABELS[quiz.quiz_type]}
        </h1>
        <a
          href={api.quizPdfUrl(quizId)}
          className="mb-4 inline-block text-xs text-brand-500 hover:underline"
        >
          Download quiz as PDF
        </a>

        <div className="mb-6">
          <ProgressBar current={answeredCount} total={quiz.questions.length} />
        </div>

        {quiz.questions.map((question, index) => {
          const answer = answers[String(question.id)];

          return (
            <QuestionCard key={question.id} index={index + 1} question={question.question} answered={answer !== undefined}>
              {quiz.quiz_type === "mcq" && (
                <div>
                  {question.options.map((option) => (
                    <OptionButton
                      key={option}
                      label={option}
                      selected={answer === option}
                      onClick={() => setAnswer(question.id, option)}
                    />
                  ))}
                </div>
              )}

              {quiz.quiz_type === "tf" && (
                <div>
                  <OptionButton label="True" selected={answer === true} onClick={() => setAnswer(question.id, true)} />
                  <OptionButton label="False" selected={answer === false} onClick={() => setAnswer(question.id, false)} />
                </div>
              )}

              {quiz.quiz_type === "fib" && (
                <input
                  type="text"
                  value={answer || ""}
                  onChange={(event) => setAnswer(question.id, event.target.value)}
                  placeholder="Your answer"
                  className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:border-brand-400"
                  style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
                />
              )}
            </QuestionCard>
          );
        })}

        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}

        <button
          type="button"
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full rounded-lg bg-brand-500 py-2.5 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {submitting ? "Submitting..." : "Submit Answers"}
        </button>
      </Card>
    </div>
  );
}
