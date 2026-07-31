import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import OptionButton from "../OptionButton.jsx";

describe("OptionButton", () => {
  it("renders its label and calls onClick when clicked", () => {
    const onClick = vi.fn();
    render(<OptionButton label="Replication" selected={false} onClick={onClick} />);

    const button = screen.getByRole("button", { name: "Replication" });
    fireEvent.click(button);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("applies a distinct style when selected", () => {
    render(<OptionButton label="Replication" selected onClick={() => {}} />);
    const button = screen.getByRole("button", { name: "Replication" });
    expect(button.className).toContain("border-brand-500");
  });
});
