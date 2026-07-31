import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import QuestionCard from "../QuestionCard.jsx";

describe("QuestionCard", () => {
  it("renders the question index and text", () => {
    render(
      <QuestionCard index={2} question="What enables scaling?">
        <p>answer control</p>
      </QuestionCard>
    );

    expect(screen.getByText(/2\./)).toBeInTheDocument();
    expect(screen.getByText(/What enables scaling\?/)).toBeInTheDocument();
    expect(screen.getByText("answer control")).toBeInTheDocument();
  });

  it("shows an answered indicator only when answered", () => {
    const { rerender } = render(
      <QuestionCard index={1} question="Q" answered={false}>
        <span />
      </QuestionCard>
    );
    expect(screen.queryByText(/answered/)).not.toBeInTheDocument();

    rerender(
      <QuestionCard index={1} question="Q" answered>
        <span />
      </QuestionCard>
    );
    expect(screen.getByText(/answered/)).toBeInTheDocument();
  });
});
