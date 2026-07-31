import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Card from "../components/Card.jsx";
import Spinner from "../components/Spinner.jsx";
import { api } from "../api/client.js";
import { useSessionId } from "../context/SessionContext.jsx";

const TYPE_LABELS = { mcq: "Multiple Choice", fib: "Fill in the Blanks", tf: "True or False" };

export default function HistoryPage() {
  const sessionId = useSessionId();
  const [attempts, setAttempts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .getSessionAttempts(sessionId)
      .then(setAttempts)
      .catch((err) => setError(err.message));
  }, [sessionId]);

  const chartData = (attempts || []).map((entry, index) => ({
    attempt: index + 1,
    percentage: entry.total ? Math.round((entry.score / entry.total) * 100) : 0,
  }));

  return (
    <div className="flex justify-center px-4 py-8">
      <Card className="w-full max-w-2xl p-6">
        <h1 className="mb-4 text-xl font-bold">📊 Score History</h1>

        {error && <p className="text-sm text-red-500">{error}</p>}
        {!attempts && !error && <Spinner label="Loading your history..." />}

        {attempts && attempts.length === 0 && (
          <p className="text-sm" style={{ color: "var(--text-muted)" }}>
            No quiz attempts yet on this device. Upload a document and take a quiz to see your progress here.
          </p>
        )}

        {attempts && attempts.length > 0 && (
          <>
            {attempts.length > 1 && (
              <div className="mb-6">
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="attempt" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Line type="monotone" dataKey="percentage" stroke="#2b6777" strokeWidth={2} dot />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <ul className="space-y-2">
              {attempts.map((attempt) => (
                <li
                  key={attempt.id}
                  className="flex items-center justify-between rounded-lg p-3 text-sm"
                  style={{ background: "var(--surface-muted)" }}
                >
                  <span>{TYPE_LABELS[attempt.quiz_type] || attempt.quiz_type}</span>
                  <span className="font-semibold">
                    {attempt.score}/{attempt.total} ({attempt.total ? Math.round((attempt.score / attempt.total) * 100) : 0}%)
                  </span>
                </li>
              ))}
            </ul>
          </>
        )}
      </Card>
    </div>
  );
}
