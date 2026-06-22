import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import * as api from "./api/client.js";

vi.mock("./api/client.js", async () => {
  const actual = await vi.importActual("./api/client.js");
  return {
    ...actual,
    createCheck: vi.fn(),
    fetchRecentChecks: vi.fn()
  };
});

const createdCheck = {
  id: 42,
  company_name: "Northwind Supply BV",
  tax_id: "NL12345678B01",
  country: "NL",
  risk_score: 16,
  severity: "low",
  summary: "Northwind Supply BV is rated low based on 1 signal(s). Primary indicators: registry: Recent corporate profile change indicator.",
  signals: [
    {
      source: "registry",
      title: "Recent corporate profile change indicator",
      score: 16,
      details: "signal details"
    }
  ],
  created_at: "2026-04-15T12:00:00Z"
};

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.fetchRecentChecks.mockResolvedValue({ items: [] });
  });

  it("submits a screening request and renders the returned result", async () => {
    api.createCheck.mockResolvedValue(createdCheck);

    render(<App />);

    await screen.findByText("No checks yet");

    fireEvent.change(screen.getByLabelText("Company name"), {
      target: { name: "company_name", value: "  Northwind Supply BV  " }
    });
    fireEvent.change(screen.getByLabelText("Tax ID"), {
      target: { name: "tax_id", value: " nl12345678b01 " }
    });
    fireEvent.change(screen.getByLabelText("Country"), {
      target: { name: "country", value: "nl" }
    });

    fireEvent.click(screen.getByRole("button", { name: "Run check" }));

    await waitFor(() => {
      expect(api.createCheck).toHaveBeenCalledWith(
        {
          company_name: "Northwind Supply BV",
          tax_id: "nl12345678b01",
          country: "NL"
        },
        expect.any(AbortSignal)
      );
    });

    expect(await screen.findByRole("heading", { name: "Northwind Supply BV" })).toBeTruthy();
    expect(screen.getByText(/Primary indicators:/)).toBeTruthy();
    expect(screen.getByText("LOW · 16")).toBeTruthy();
    expect(screen.getByText("Signal count")).toBeTruthy();
  });

  it("renders API validation errors returned from submission", async () => {
    api.createCheck.mockRejectedValue(new Error("company_name: Field required country: Value error"));

    render(<App />);

    await screen.findByText("No checks yet");

    fireEvent.change(screen.getByLabelText("Company name"), {
      target: { name: "company_name", value: "Example Company" }
    });

    fireEvent.click(screen.getByRole("button", { name: "Run check" }));

    expect(await screen.findByText("company_name: Field required country: Value error")).toBeTruthy();
  });
});
