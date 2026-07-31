import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Card from "../components/Card.jsx";
import { api } from "../api/client.js";
import { useSessionId } from "../context/SessionContext.jsx";

const TYPE_LABELS = { mcq: "Multiple Choice Questions", fib: "Fill in the Blanks", tf: "True or False" };

export default function ResultsPage() {
  const { quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const sessionId = useSessionId();

  const { quiz, attempt } = location.state || {};
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api
      .getSessionAttempts(sessionId)
      .then((attempts) =>
        setHistory(
          attempts.map((entry, index) => ({
            attempt: index + 1,
            percentage: entry.total ? Math.round((entry.score / entry.total) * 100) : 0,
          }))
        )
      )
      .catch(() => setHistory([]));
  }, [sessionId]);

  if (!quiz || !attempt) {
    return (
      <div className="mx-auto max-w-lg px-4 py-10 text-center text-white">
        <p>Results are unavailable (e.g. after a page refresh).</p>
        <button onClick={() => navigate("/")} className="mt-4 underline">
          Start a new quiz
        </button>
      </div>
    );
  }

  const percentage = attempt.total ? Math.round((attempt.score / attempt.total) * 100) : 0;

  return (
    <div className="flex justify-center px-4 py-8">
      <Card className="w-full max-w-2xl p-6">
        <h1 className="mb-1 flex items-center gap-2 text-xl font-bold">📝 Results</h1>
        <p className="mb-4 text-sm" style={{ color: "var(--text-muted)" }}>{TYPE_LABELS[quiz.quiz_type]}</p>

        <div className="mb-6 rounded-xl p-4" style={{ background: "var(--surface-muted)" }}>
          <p className="text-3xl font-bold text-brand-500">
            {attempt.score} / {attempt.total} <span className="text-lg font-medium">({percentage}%)</span>
          </p>
        </div>

        {history.length > 1 && (
          <div className="mb-6">
            <h2 className="mb-2 text-sm font-semibold">Progress over time</h2>
            <ResponsiveContainer width="100%" height={160}>
              <LineChart data={history}>
                <XAxis dataKey="attempt" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Line type="monotone" dataKey="percentage" stroke="#2b6777" strokeWidth={2} dot />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="mb-6 flex gap-3">
          <a
            href={api.resultsPdfUrl(quizId, attempt.id)}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
          >
            Download Results PDF
          </a>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="rounded-lg border px-4 py-2 text-sm font-semibold"
            style={{ borderColor: "var(--border)" }}
          >
            New Quiz
          </button>
        </div>

        <div>
          {attempt.breakdown.map((item, index) => (
            <div key={item.question_id} className="border-b py-4 first:pt-0 last:border-b-0" style={{ borderColor: "var(--border)" }}>
              <h3 className="mb-1 font-semibold">{index + 1}. {item.question}</h3>
              <p className={item.is_correct ? "text-sm text-emerald-500" : "text-sm text-red-500"}>
                Your answer: {item.submitted_answer === null || item.submitted_answer === undefined
                  ? "(no answer)"
                  : String(item.submitted_answer)}
                {!item.is_correct && ` — Correct answer: ${item.correct_answer}`}
              </p>
              {item.explanation && (
                <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>{item.explanation}</p>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
