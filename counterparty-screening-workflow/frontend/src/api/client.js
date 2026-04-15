const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

export function formatApiError(payload) {
  const detail = payload?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : "field";
        const message = typeof item?.msg === "string" ? item.msg : "Invalid value.";
        return `${field}: ${message}`;
      })
      .join(" ");
  }

  return "The request failed. Please review the form data and try again.";
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new Error(formatApiError(payload));
  }

  return payload;
}

export async function createCheck(input, signal) {
  const response = await fetch(`${API_URL}/checks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input),
    signal
  });

  return parseResponse(response);
}

export async function fetchRecentChecks(signal) {
  const response = await fetch(`${API_URL}/checks?limit=5&offset=0`, {
    headers: {
      Accept: "application/json"
    },
    signal
  });

  return parseResponse(response);
}
