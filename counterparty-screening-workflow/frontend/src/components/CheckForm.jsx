const examples = [
  {
    label: "Trade-heavy profile",
    value: {
      company_name: "Harbor Freight Solutions",
      tax_id: "SG-20455678",
      country: "SG"
    }
  },
  {
    label: "Lower-signal profile",
    value: {
      company_name: "Northwind Consulting",
      tax_id: "DE-5523419",
      country: "DE"
    }
  }
];

export default function CheckForm({ form, disabled, onChange, onSubmit, onUseExample }) {
  return (
    <form className="check-form" onSubmit={onSubmit}>
      <div className="example-row" aria-label="Quick examples">
        {examples.map((example) => (
          <button
            key={example.label}
            type="button"
            className="secondary-button"
            onClick={() => onUseExample(example.value)}
            disabled={disabled}
          >
            {example.label}
          </button>
        ))}
      </div>

      <label className="field">
        <span>Company name</span>
        <input
          name="company_name"
          value={form.company_name}
          onChange={onChange}
          placeholder="Northwind Consulting"
          autoComplete="organization"
          required
        />
      </label>

      <div className="field-grid">
        <label className="field">
          <span>Tax ID</span>
          <input
            name="tax_id"
            value={form.tax_id}
            onChange={onChange}
            placeholder="DE-5523419"
            autoComplete="off"
          />
        </label>

        <label className="field">
          <span>Country</span>
          <input
            name="country"
            value={form.country}
            onChange={onChange}
            placeholder="DE"
            maxLength={2}
            autoComplete="country"
          />
        </label>
      </div>

      <div className="form-actions">
        <button className="primary-button" type="submit" disabled={disabled || !form.company_name.trim()}>
          {disabled ? "Running check..." : "Run check"}
        </button>
        <p className="form-note">Saved results appear in the recent checks panel for quick comparison.</p>
      </div>
    </form>
  );
}
