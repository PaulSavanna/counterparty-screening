# Signal model

The screening workflow uses deterministic surrogate signals so the same input produces the same result locally, in tests, and in CI.

## Signal sources

### Registry
- missing tax or registration identifier
- trade-heavy or logistics-oriented company name
- hashed profile bucket indicating recent corporate profile change or ownership complexity

### Sanctions
- trade-oriented company name combined with a higher-risk jurisdiction
- deterministic name-screening similarity match for some profiles

### Litigation
- legal-distress keywords in the company name
- hashed profile bucket indicating repeated dispute metadata

### News
- adverse-media keywords in the company name

## Scoring rules

- signals are grouped by source
- the strongest signal from each source is counted in full
- additional signals from the same source are discounted
- each source has a maximum contribution cap
- agreement across several sources adds a small escalation bonus
- sanctions signals combined with news or litigation add an extra escalation bonus

The model favors reproducibility and explainability over live-source coverage and real-time data collection.
