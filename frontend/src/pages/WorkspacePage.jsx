import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import Card from "../components/Card.jsx";
import ChatPanel from "../components/ChatPanel.jsx";
import DocumentSummary from "../components/DocumentSummary.jsx";
import RelatedDocuments from "../components/RelatedDocuments.jsx";
import { api } from "../api/client.js";

const QUIZ_TYPES = [
  { key: "mcq", label: "Multiple Choice" },
  { key: "fib", label: "Fill in the Blanks" },
  { key: "tf", label: "True or False" },
];
const DIFFICULTIES = ["easy", "medium", "hard"];

export default function WorkspacePage() {
  const { documentId } = useParams();
  const navigate = useNavigate();

  const [quizType, setQuizType] = useState("mcq");
  const [difficulty, setDifficulty] = useState("medium");
  const [count, setCount] = useState(5);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const generateQuiz = async () => {
    setGenerating(true);
    setError(null);
    try {
      const quiz = await api.generateQuiz(documentId, quizType, { count, difficulty });
      navigate(`/quiz/${quiz.id}`, { state: { quiz } });
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <Card className="p-6">
          <DocumentSummary documentId={documentId} />
        </Card>

        <Card className="p-6">
          <h2 className="mb-4 font-semibold">📝 Generate a Quiz</h2>

          <div className="mb-4 flex flex-wrap gap-2">
            {QUIZ_TYPES.map((type) => (
              <button
                key={type.key}
                type="button"
                onClick={() => setQuizType(type.key)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                  quizType === type.key ? "bg-brand-500 text-white" : ""
                }`}
                style={quizType === type.key ? undefined : { background: "var(--surface-muted)", color: "var(--text-muted)" }}
              >
                {type.label}
              </button>
            ))}
          </div>

          <div className="mb-4 flex flex-wrap items-center gap-4 text-sm">
            {quizType === "mcq" && (
              <label className="flex items-center gap-2">
                Difficulty
                <select
                  value={difficulty}
                  onChange={(event) => setDifficulty(event.target.value)}
                  className="rounded-lg border px-2 py-1"
                  style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
                >
                  {DIFFICULTIES.map((level) => (
                    <option key={level} value={level}>
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <label className="flex items-center gap-2">
              Questions
              <input
                type="number"
                min={1}
                max={10}
                value={count}
                onChange={(event) => setCount(Number(event.target.value))}
                className="w-16 rounded-lg border px-2 py-1"
                style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
              />
            </label>
          </div>

          {error && <p className="mb-3 text-sm text-red-500">{error}</p>}

          <button
            type="button"
            onClick={generateQuiz}
            disabled={generating}
            className="rounded-lg bg-brand-500 px-5 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {generating ? "Generating..." : "Generate Quiz"}
          </button>
        </Card>

        <Card className="p-6">
          <RelatedDocuments documentId={documentId} />
        </Card>
      </div>

      <Card className="h-[600px] p-6 lg:sticky lg:top-6">
        <ChatPanel documentId={documentId} />
      </Card>
    </div>
  );
}
