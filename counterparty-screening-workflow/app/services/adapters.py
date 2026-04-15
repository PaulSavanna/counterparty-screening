from __future__ import annotations

import hashlib
import re
from collections.abc import Callable

from app.schemas.check import CheckCreate, RiskSignal

Adapter = Callable[[CheckCreate], list[RiskSignal]]

HIGH_RISK_JURISDICTIONS = {"BY", "IR", "KP", "RU", "SY"}
TRANSPORT_TERMS = ("cargo", "freight", "logistics", "shipping")
COMPLEX_STRUCTURE_TERMS = (
    "group",
    "holding",
    "holdings",
    "international",
    "ventures",
)
TRADE_SCREENING_TERMS = ("export", "global", "import", "trade", "trading")
LEGAL_DISTRESS_TERMS = ("claim", "debt", "default", "insolv", "lawsuit")
ADVERSE_MEDIA_TERMS = ("bankrupt", "default", "debt", "fraud", "risk")


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip().casefold())


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    normalized = _normalize_text(text)
    return any(phrase in normalized for phrase in phrases)


def _fingerprint_bucket(payload: CheckCreate, modulo: int = 100) -> int:
    fingerprint = "|".join(
        [
            _normalize_text(payload.company_name),
            payload.tax_id or "",
            payload.country or "",
        ]
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def registry_adapter(payload: CheckCreate) -> list[RiskSignal]:
    signals: list[RiskSignal] = []
    bucket = _fingerprint_bucket(payload)

    if not payload.tax_id:
        signals.append(
            RiskSignal(
                source="registry",
                title="Incomplete legal identifier set",
                score=12,
                details=(
                    "The request does not include a tax or registration identifier, which limits "
                    "basic ownership and registry verification."
                ),
            )
        )

    if _contains_any(payload.company_name, TRANSPORT_TERMS):
        signals.append(
            RiskSignal(
                source="registry",
                title="Trade and logistics operating profile",
                score=8,
                details=(
                    "The company name points to a trade-heavy operating profile where onboarding "
                    "usually requires tighter ownership and route screening."
                ),
            )
        )

    if _contains_any(payload.company_name, COMPLEX_STRUCTURE_TERMS) or bucket < 24:
        signals.append(
            RiskSignal(
                source="registry",
                title="Recent corporate profile change indicator",
                score=16,
                details=(
                    "The deterministic registry surrogate suggests a recent legal-profile "
                    "change or ownership-complexity marker that would justify analyst review."
                ),
            )
        )

    return signals


def sanctions_adapter(payload: CheckCreate) -> list[RiskSignal]:
    bucket = _fingerprint_bucket(payload)
    requires_screening = _contains_any(payload.company_name, TRADE_SCREENING_TERMS)
    country = payload.country or ""

    if country in HIGH_RISK_JURISDICTIONS and requires_screening:
        return [
            RiskSignal(
                source="sanctions",
                title="Jurisdiction and trade-screening escalation",
                score=38,
                details=(
                    "The input combines a trade-oriented profile with a jurisdiction that would "
                    "normally require enhanced sanctions and export-control screening."
                ),
            )
        ]

    if requires_screening and bucket < 16:
        return [
            RiskSignal(
                source="sanctions",
                title="Name-screening similarity warning",
                score=30,
                details=(
                    "The deterministic screening surrogate produced a match pattern that should "
                    "be reviewed before the counterparty is approved."
                ),
            )
        ]

    return []


def litigation_adapter(payload: CheckCreate) -> list[RiskSignal]:
    bucket = _fingerprint_bucket(payload)
    if _contains_any(payload.company_name, LEGAL_DISTRESS_TERMS) or bucket < 22:
        return [
            RiskSignal(
                source="litigation",
                title="Repeated dispute metadata",
                score=22,
                details=(
                    "The litigation surrogate indicates recurring dispute activity over the "
                    "lookback window, which would normally trigger a legal follow-up."
                ),
            )
        ]
    return []


def news_adapter(payload: CheckCreate) -> list[RiskSignal]:
    if _contains_any(payload.company_name, ADVERSE_MEDIA_TERMS):
        return [
            RiskSignal(
                source="news",
                title="Adverse media keyword match",
                score=24,
                details=(
                    "The adverse-media surrogate found financially negative language associated "
                    "with the entity name and should be reviewed before approval."
                ),
            )
        ]
    return []


ADAPTERS: tuple[Adapter, ...] = (
    registry_adapter,
    sanctions_adapter,
    litigation_adapter,
    news_adapter,
)


def collect_signals(payload: CheckCreate) -> list[RiskSignal]:
    unique_signals: dict[tuple[str, str], RiskSignal] = {}

    for adapter in ADAPTERS:
        for signal in adapter(payload):
            unique_signals[(signal.source, signal.title)] = signal

    return sorted(
        unique_signals.values(),
        key=lambda signal: (-signal.score, signal.source, signal.title),
    )
