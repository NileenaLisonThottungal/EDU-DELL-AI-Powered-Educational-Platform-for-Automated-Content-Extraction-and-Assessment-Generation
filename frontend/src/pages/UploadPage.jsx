import { useRef, useState } from "react";
import { useNavigate } from "react-router";
import Card from "../components/Card.jsx";
import Spinner from "../components/Spinner.jsx";
import { api } from "../api/client.js";

const TABS = [
  { key: "file", label: "Upload File" },
  { key: "url", label: "From URL" },
  { key: "text", label: "Paste Text" },
];

export default function UploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState("file");
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) setFile(dropped);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    if (activeTab === "file" && !file) return setError("Choose a file first.");
    if (activeTab === "url" && !url.trim()) return setError("Enter a URL first.");
    if (activeTab === "text" && !text.trim()) return setError("Paste some text first.");

    setSubmitting(true);
    try {
      const document =
        activeTab === "file"
          ? await api.uploadFile(file)
          : activeTab === "url"
            ? await api.uploadUrl(url.trim())
            : await api.uploadText(text.trim());

      navigate(`/workspace/${document.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex justify-center px-4 py-10">
      <Card className="w-full max-w-lg p-8">
        <h1 className="mb-1 text-2xl font-bold">Welcome to EDU-DELL</h1>
        <p className="mb-6 text-sm" style={{ color: "var(--text-muted)" }}>
          Explore your revision — upload a document, a link, or paste text to get a summary, a chatbot, and
          auto-generated quizzes.
        </p>

        <div className="mb-6 flex gap-1 rounded-lg p-1" style={{ background: "var(--surface-muted)" }}>
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === tab.key ? "bg-brand-500 text-white" : ""
              }`}
              style={activeTab === tab.key ? undefined : { color: "var(--text-muted)" }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {activeTab === "file" && (
            <div
              onDragOver={(event) => {
                event.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center text-sm transition-colors ${
                dragActive ? "border-brand-500" : ""
              }`}
              style={{ borderColor: dragActive ? undefined : "var(--border)", color: "var(--text-muted)" }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.pptx,.txt"
                className="hidden"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
              {file ? (
                <p className="font-medium" style={{ color: "var(--text)" }}>{file.name}</p>
              ) : (
                <>
                  <p>Drag and drop your PDF, DOCX, PPTX, or TXT file here</p>
                  <p className="mt-1">or click to select</p>
                </>
              )}
            </div>
          )}

          {activeTab === "url" && (
            <input
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com/article"
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:border-brand-400"
              style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
            />
          )}

          {activeTab === "text" && (
            <textarea
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste your study material here..."
              rows={6}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:border-brand-400"
              style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
            />
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-brand-500 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-600 disabled:opacity-50"
          >
            {submitting ? "Processing..." : "Upload & Create Quiz"}
          </button>
          {submitting && <Spinner label="Extracting and indexing your document..." />}
        </form>
      </Card>
    </div>
  );
}
