function formatDate(isoString) {
  const date = new Date(isoString);
  return Number.isNaN(date.getTime()) ? isoString : date.toLocaleString();
}

function getScoreWidth(score) {
  const normalized = Math.max(0, Math.min(100, Number(score) || 0));
  return `${normalized}%`;
}

function getTopSignalSource(signals) {
  if (!signals.length) {
    return "—";
  }
  return signals[0].source;
}

export default function CheckResultCard({ result }) {
  if (!result) {
    return (
      <section className="card result-card result-card--empty">
        <p className="eyebrow">Latest result</p>
        <h2>No checks yet</h2>
        <p className="muted">
          Submit a counterparty to review the score, supporting signals, and saved result history.
        </p>
      </section>
    );
  }

  const severityClassName = `severity-pill severity-pill--${result.severity}`;

  return (
    <section className="card result-card" aria-live="polite">
      <div className="result-header">
        <div>
          <p className="eyebrow">Latest result</p>
          <h2>{result.company_name}</h2>
          <p className="muted">Created {formatDate(result.created_at)}</p>
        </div>
        <div className={severityClassName}>
          {result.severity.toUpperCase()} · {result.risk_score.toFixed(0)}
        </div>
      </div>

      <div className="score-meter" aria-label={`Risk score ${result.risk_score.toFixed(0)} out of 100`}>
        <div className="score-meter__track">
          <div className={`score-meter__fill score-meter__fill--${result.severity}`} style={{ width: getScoreWidth(result.risk_score) }} />
        </div>
        <div className="score-meter__labels">
          <span>0</span>
          <span>100</span>
        </div>
      </div>

      <p className="summary">{result.summary}</p>

      <div className="metadata-grid">
        <div>
          <span className="metadata-label">Country</span>
          <strong>{result.country || "—"}</strong>
        </div>
        <div>
          <span className="metadata-label">Tax ID</span>
          <strong>{result.tax_id || "—"}</strong>
        </div>
        <div>
          <span className="metadata-label">Top signal source</span>
          <strong>{getTopSignalSource(result.signals)}</strong>
        </div>
        <div>
          <span className="metadata-label">Signal count</span>
          <strong>{result.signals.length}</strong>
        </div>
      </div>

      <div>
        <h3>Risk signals</h3>
        {result.signals.length === 0 ? (
          <p className="muted">No material risk signals were returned.</p>
        ) : (
          <ul className="signal-list">
            {result.signals.map((signal) => (
              <li key={`${signal.source}-${signal.title}`} className="signal-item">
                <div className="signal-header">
                  <strong>{signal.title}</strong>
                  <span>
                    {signal.source} · {signal.score}
                  </span>
                </div>
                <p>{signal.details}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
