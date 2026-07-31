import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "../../api/client.js";
import UploadPage from "../UploadPage.jsx";

const navigateMock = vi.fn();

vi.mock("react-router", async () => {
  const actual = await vi.importActual("react-router");
  return { ...actual, useNavigate: () => navigateMock };
});

vi.mock("../../api/client.js", () => ({
  api: {
    uploadFile: vi.fn(),
    uploadUrl: vi.fn(),
    uploadText: vi.fn(),
  },
}));

beforeEach(() => {
  navigateMock.mockClear();
  vi.clearAllMocks();
});

function renderUploadPage() {
  return render(
    <MemoryRouter>
      <UploadPage />
    </MemoryRouter>
  );
}

describe("UploadPage", () => {
  it("submits pasted text and navigates to the workspace", async () => {
    api.uploadText.mockResolvedValue({ id: "doc-1" });
    renderUploadPage();

    fireEvent.click(screen.getByRole("button", { name: "Paste Text" }));
    fireEvent.change(screen.getByPlaceholderText(/Paste your study material/i), {
      target: { value: "Some study notes." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Upload & Create Quiz" }));

    await waitFor(() => expect(api.uploadText).toHaveBeenCalledWith("Some study notes."));
    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("/workspace/doc-1"));
  });

  it("shows an error instead of submitting when text is empty", async () => {
    renderUploadPage();

    fireEvent.click(screen.getByRole("button", { name: "Paste Text" }));
    fireEvent.click(screen.getByRole("button", { name: "Upload & Create Quiz" }));

    expect(await screen.findByText("Paste some text first.")).toBeInTheDocument();
    expect(api.uploadText).not.toHaveBeenCalled();
  });

  it("submits a URL on the URL tab", async () => {
    api.uploadUrl.mockResolvedValue({ id: "doc-2" });
    renderUploadPage();

    fireEvent.click(screen.getByRole("button", { name: "From URL" }));
    fireEvent.change(screen.getByPlaceholderText(/example.com/i), {
      target: { value: "https://example.com/article" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Upload & Create Quiz" }));

    await waitFor(() => expect(api.uploadUrl).toHaveBeenCalledWith("https://example.com/article"));
    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("/workspace/doc-2"));
  });
});
