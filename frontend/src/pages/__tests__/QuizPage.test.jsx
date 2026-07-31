import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SessionProvider } from "../../context/SessionContext.jsx";
import { api } from "../../api/client.js";
import QuizPage from "../QuizPage.jsx";

const navigateMock = vi.fn();

vi.mock("react-router", async () => {
  const actual = await vi.importActual("react-router");
  return { ...actual, useNavigate: () => navigateMock };
});

vi.mock("../../api/client.js", () => ({
  api: {
    submitQuiz: vi.fn(),
    quizPdfUrl: vi.fn(() => "http://localhost:5000/api/quiz/quiz-1/export.pdf"),
  },
}));

beforeEach(() => {
  navigateMock.mockClear();
  vi.clearAllMocks();
});

const mcqQuiz = {
  id: "quiz-1",
  quiz_type: "mcq",
  questions: [
    { id: 1, question: "What enables scaling?", options: ["Replication", "Deletion", "Caching", "Sorting"], correct_answer: "Replication" },
  ],
};

function renderQuizPage(quiz) {
  return render(
    <SessionProvider>
      <MemoryRouter initialEntries={[{ pathname: "/quiz/quiz-1", state: { quiz } }]}>
        <Routes>
          <Route path="/quiz/:quizId" element={<QuizPage />} />
        </Routes>
      </MemoryRouter>
    </SessionProvider>
  );
}

describe("QuizPage", () => {
  it("lets the user select an MCQ option and submit", async () => {
    api.submitQuiz.mockResolvedValue({ id: "attempt-1", score: 1, total: 1, breakdown: [] });
    renderQuizPage(mcqQuiz);

    expect(screen.getByText("Answered 0/1")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Replication" }));
    expect(screen.getByText("Answered 1/1")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Submit Answers" }));

    await waitFor(() =>
      expect(api.submitQuiz).toHaveBeenCalledWith("quiz-1", { "1": "Replication" }, expect.any(String))
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith(
        "/results/quiz-1",
        expect.objectContaining({ state: expect.objectContaining({ quiz: mcqQuiz }) })
      )
    );
  });

  it("shows a recovery message when quiz state is missing", () => {
    renderQuizPage(undefined);
    expect(screen.getByText(/quiz session was lost/i)).toBeInTheDocument();
  });
});
