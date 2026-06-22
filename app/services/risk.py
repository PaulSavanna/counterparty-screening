from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from app.core.config import get_settings
from app.schemas.check import RiskSignal, Severity

SECONDARY_SIGNAL_FACTOR = 0.6
CROSS_SOURCE_BONUS = 8
ESCALATION_BONUS = 10

SOURCE_CAPS = {
    "registry": 24,
    "sanctions": 40,
    "litigation": 26,
    "news": 24,
}


def calculate_risk(signals: Sequence[RiskSignal]) -> tuple[float, Severity]:
    settings = get_settings()
    grouped_scores: dict[str, list[int]] = defaultdict(list)

    for signal in signals:
        grouped_scores[signal.source].append(signal.score)

    weighted_score = 0.0
    sources_present = set(grouped_scores)

    for source, scores in grouped_scores.items():
        ordered_scores = sorted(scores, reverse=True)
        primary_score = float(ordered_scores[0])
        secondary_score = sum(score * SECONDARY_SIGNAL_FACTOR for score in ordered_scores[1:])
        weighted_source_score = primary_score + secondary_score
        source_cap = SOURCE_CAPS.get(source, settings.max_risk_score)
        weighted_score += min(weighted_source_score, source_cap)

    if len(sources_present) >= 3:
        weighted_score += CROSS_SOURCE_BONUS

    if "sanctions" in sources_present and ({"news", "litigation"} & sources_present):
        weighted_score += ESCALATION_BONUS

    bounded_score = float(min(round(weighted_score, 1), settings.max_risk_score))

    if bounded_score >= settings.risk_high_threshold:
        return bounded_score, "high"
    if bounded_score >= settings.risk_medium_threshold:
        return bounded_score, "medium"
    return bounded_score, "low"
