import { useCallback, useEffect, useRef, useState } from "react";

import { createCheck, fetchRecentChecks } from "./api/client.js";
import CheckForm from "./components/CheckForm.jsx";
import CheckResultCard from "./components/CheckResultCard.jsx";
import FeedbackBanner from "./components/FeedbackBanner.jsx";
import RecentChecksPanel from "./components/RecentChecksPanel.jsx";

const initialForm = {
  company_name: "",
  tax_id: "",
  country: ""
};

export default function App() {
  const submitAbortControllerRef = useRef(null);
  const historyAbortControllerRef = useRef(null);

  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [recentChecks, setRecentChecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  const loadRecentChecks = useCallback(async () => {
    historyAbortControllerRef.current?.abort();
    const controller = new AbortController();
    historyAbortControllerRef.current = controller;
    setHistoryLoading(true);

    try {
      const data = await fetchRecentChecks(controller.signal);
      setRecentChecks(data.items || []);
      if (!result && data.items?.length) {
        setResult(data.items[0]);
      }
    } catch (requestError) {
      if (requestError.name !== "AbortError") {
        setError(requestError.message || "Unable to load recent checks.");
      }
    } finally {
      setHistoryLoading(false);
    }
  }, [result]);

  useEffect(() => {
    void loadRecentChecks();

    return () => {
      submitAbortControllerRef.current?.abort();
      historyAbortControllerRef.current?.abort();
    };
  }, [loadRecentChecks]);

  function handleInputChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name === "country" ? value.toUpperCase() : value
    }));
  }

  function handleUseExample(nextForm) {
    setForm(nextForm);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    submitAbortControllerRef.current?.abort();
    const controller = new AbortController();
    submitAbortControllerRef.current = controller;

    setLoading(true);
    setError("");

    try {
      const payload = {
        company_name: form.company_name.trim(),
        tax_id: form.tax_id.trim() || null,
        country: form.country.trim() || null
      };
      const data = await createCheck(payload, controller.signal);
      setResult(data);
      setRecentChecks((current) => [data, ...current.filter((item) => item.id !== data.id)].slice(0, 5));
    } catch (submitError) {
      if (submitError.name !== "AbortError") {
        setError(submitError.message || "Unable to run the check.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero card">
        <div className="hero-grid">
          <div>
            <p className="eyebrow">Full-stack screening workflow</p>
            <h1>Counterparty Screening Workflow</h1>
            <p className="hero-copy">
              Run a deterministic counterparty screening check, review the collected signals, and
              inspect persisted results from the latest requests.
            </p>
          </div>
          <div className="hero-stats" aria-label="Project highlights">
            <div>
              <strong>FastAPI</strong>
              <span>Validated API and persistence workflow</span>
            </div>
            <div>
              <strong>React</strong>
              <span>Focused review UI for input, result, and history</span>
            </div>
            <div>
              <strong>Alembic</strong>
              <span>Versioned schema management</span>
            </div>
          </div>
        </div>

        <CheckForm
          form={form}
          disabled={loading}
          onChange={handleInputChange}
          onSubmit={handleSubmit}
          onUseExample={handleUseExample}
        />
        <FeedbackBanner tone="error" message={error} />
      </section>

      <section className="content-grid">
        <CheckResultCard result={result} />
        <RecentChecksPanel checks={recentChecks} loading={historyLoading} onSelect={setResult} />
      </section>
    </main>
  );
}
