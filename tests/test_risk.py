from app.schemas.check import CheckCreate, RiskSignal
from app.services.counterparty_service import run_counterparty_check
from app.services.risk import calculate_risk
from app.services.summary import generate_summary


def test_counterparty_check_returns_signals_and_summary():
    payload = CheckCreate(company_name="Global Cargo Risk", tax_id="7701234567", country="RU")
    result = run_counterparty_check(payload)

    assert result.risk_score == 100.0
    assert result.severity == "high"
    assert "Global Cargo Risk" in result.summary
    assert len(result.signals) == 5


def test_calculate_risk_discounts_repeated_signals_and_adds_cross_source_bonus():
    signals = [
        RiskSignal(source="registry", title="Registry alert", score=16, details="signal one"),
        RiskSignal(source="registry", title="Registry flag", score=8, details="signal two"),
        RiskSignal(
            source="sanctions",
            title="Screening escalation",
            score=30,
            details="signal three",
        ),
        RiskSignal(source="news", title="Adverse media", score=20, details="signal four"),
    ]

    score, severity = calculate_risk(signals)

    assert score == 88.8
    assert severity == "high"


def test_generate_summary_is_deterministic_and_grounded_in_signals():
    summary = generate_summary(
        company_name="Northwind Supply BV",
        severity="medium",
        signals=[
            RiskSignal(
                source="registry",
                title="Recent corporate profile change indicator",
                score=16,
                details="signal details",
            ),
            RiskSignal(
                source="litigation",
                title="Repeated dispute metadata",
                score=22,
                details="signal details",
            ),
        ],
    )

    assert "Northwind Supply BV" in summary
    assert "registry: Recent corporate profile change indicator" in summary
    assert "litigation: Repeated dispute metadata" in summary
