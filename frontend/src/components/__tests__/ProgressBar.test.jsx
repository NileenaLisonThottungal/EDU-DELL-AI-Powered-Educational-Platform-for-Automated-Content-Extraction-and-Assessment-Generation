import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ProgressBar from "../ProgressBar.jsx";

describe("ProgressBar", () => {
  it("renders the answered count and percentage", () => {
    render(<ProgressBar current={2} total={4} />);
    expect(screen.getByText("Answered 2/4")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("handles a zero total without dividing by zero", () => {
    render(<ProgressBar current={0} total={0} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});
