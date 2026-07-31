import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SessionProvider } from "../../context/SessionContext.jsx";
import { api } from "../../api/client.js";
import ResultsPage from "../ResultsPage.jsx";

vi.mock("../../api/client.js", () => ({
  api: {
    getSessionAttempts: vi.fn(),
    resultsPdfUrl: vi.fn(() => "http://localhost:5000/api/quiz/quiz-1/results/attempt-1/export.pdf"),
  },
}));

beforeEach(() => {
  vi.clearAllMocks();
  api.getSessionAttempts.mockResolvedValue([]);
});

const quiz = { quiz_type: "mcq" };
const attempt = {
  id: "attempt-1",
  score: 3,
  total: 4,
  breakdown: [
    { question_id: 1, question: "What enables scaling?", submitted_answer: "Replication", correct_answer: "Replication", is_correct: true, explanation: "Replication enables scaling." },
    { question_id: 2, question: "What stores embeddings?", submitted_answer: "wrong", correct_answer: "ChromaDB", is_correct: false, explanation: "ChromaDB stores embeddings." },
  ],
};

function renderResultsPage() {
  return render(
    <SessionProvider>
      <MemoryRouter initialEntries={[{ pathname: "/results/quiz-1", state: { quiz, attempt } }]}>
        <Routes>
          <Route path="/results/:quizId" element={<ResultsPage />} />
        </Routes>
      </MemoryRouter>
    </SessionProvider>
  );
}

describe("ResultsPage", () => {
  it("renders the score and per-question breakdown", async () => {
    renderResultsPage();

    expect(screen.getByText("3 / 4")).toBeInTheDocument();
    expect(screen.getByText(/What enables scaling\?/)).toBeInTheDocument();
    expect(screen.getByText(/Correct answer: ChromaDB/)).toBeInTheDocument();

    await waitFor(() => expect(api.getSessionAttempts).toHaveBeenCalled());
  });
});
