from collections.abc import Sequence

from app.schemas.check import RiskSignal, Severity


def generate_summary(company_name: str, severity: Severity, signals: Sequence[RiskSignal]) -> str:
    if not signals:
        return (
            f"{company_name} produced no material screening signals in the current rule set. "
            "The record can be reviewed and reopened from the saved check history."
        )

    signal_digest = "; ".join(f"{signal.source}: {signal.title}" for signal in signals[:3])
    return (
        f"{company_name} is rated {severity} based on {len(signals)} signal(s). "
        f"Primary indicators: {signal_digest}."
    )
