function formatDate(isoString) {
  const date = new Date(isoString);
  return Number.isNaN(date.getTime()) ? isoString : date.toLocaleString();
}

export default function RecentChecksPanel({ checks, loading, onSelect }) {
  return (
    <section className="card recent-checks-card">
      <div className="panel-header">
        <div>
          <h2>Recent checks</h2>
          <p className="muted">Review previously saved results and reopen them in the main panel.</p>
        </div>
        {loading ? <span className="muted">Refreshing…</span> : null}
      </div>

      {checks.length === 0 ? (
        <p className="muted">No saved checks yet. Create one to populate this history panel.</p>
      ) : (
        <ul className="recent-checks-list">
          {checks.map((check) => (
            <li key={check.id}>
              <button className="recent-checks-item" type="button" onClick={() => onSelect(check)}>
                <div>
                  <strong>{check.company_name}</strong>
                  <p>{formatDate(check.created_at)}</p>
                </div>
                <span className={`severity-pill severity-pill--${check.severity}`}>
                  {check.severity.toUpperCase()}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
