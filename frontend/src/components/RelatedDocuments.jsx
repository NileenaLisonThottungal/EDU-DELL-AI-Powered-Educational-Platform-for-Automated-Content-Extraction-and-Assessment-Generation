import { useState } from "react";
import { api } from "../api/client.js";
import Spinner from "./Spinner.jsx";

export default function RelatedDocuments({ documentId }) {
  const [related, setRelated] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRelatedDocuments(documentId);
      setRelated(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="font-semibold">🔗 Related Documents</h2>
        <button
          type="button"
          onClick={fetchRecommendations}
          className="rounded-lg bg-brand-500 px-3 py-1 text-xs font-medium text-white hover:bg-brand-600"
        >
          Get Recommendations
        </button>
      </div>

      {loading && <Spinner label="Searching similar documents..." />}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {related && related.length === 0 && (
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          No related documents yet — upload more to build your library.
        </p>
      )}

      {related && related.length > 0 && (
        <ul className="space-y-2">
          {related.map((doc) => (
            <li key={doc.document_id} className="rounded-lg p-3 text-sm" style={{ background: "var(--surface-muted)" }}>
              <p className="font-medium">{doc.filename}</p>
              <p className="mt-1 line-clamp-2" style={{ color: "var(--text-muted)" }}>{doc.preview}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
