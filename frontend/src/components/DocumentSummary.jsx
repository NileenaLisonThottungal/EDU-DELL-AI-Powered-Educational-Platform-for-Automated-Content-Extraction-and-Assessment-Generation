import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import Spinner from "./Spinner.jsx";

export default function DocumentSummary({ documentId }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setSummary(null);
    setError(null);

    api
      .getSummary(documentId)
      .then((data) => {
        if (!cancelled) setSummary(data.summary);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, [documentId]);

  return (
    <div>
      <h2 className="mb-2 flex items-center gap-2 font-semibold">📄 Document Summary</h2>
      {error && <p className="text-sm text-red-500">{error}</p>}
      {!error && !summary && <Spinner label="Summarizing document..." />}
      {summary && <p className="text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>{summary}</p>}
    </div>
  );
}
