from app.schemas.check import CheckComputation, CheckCreate
from app.services.adapters import collect_signals
from app.services.risk import calculate_risk
from app.services.summary import generate_summary


def run_counterparty_check(payload: CheckCreate) -> CheckComputation:
    signals = collect_signals(payload)
    score, severity = calculate_risk(signals)
    summary = generate_summary(payload.company_name, severity, signals)

    return CheckComputation(
        company_name=payload.company_name,
        tax_id=payload.tax_id,
        country=payload.country,
        risk_score=score,
        severity=severity,
        signals=signals,
        summary=summary,
    )
