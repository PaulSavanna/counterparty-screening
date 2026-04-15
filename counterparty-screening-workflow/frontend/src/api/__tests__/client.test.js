import { describe, expect, it } from "vitest";

import { formatApiError } from "../client.js";

describe("formatApiError", () => {
  it("returns a plain detail message", () => {
    expect(formatApiError({ detail: "Something failed." })).toBe("Something failed.");
  });

  it("formats FastAPI validation details", () => {
    expect(
      formatApiError({
        detail: [
          { loc: ["body", "company_name"], msg: "Field required" },
          { loc: ["body", "country"], msg: "Value error" }
        ]
      })
    ).toBe("company_name: Field required country: Value error");
  });

  it("falls back to a generic message", () => {
    expect(formatApiError({})).toContain("Please review the form data");
  });
});
