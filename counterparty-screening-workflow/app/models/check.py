from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CheckResult(Base):
    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    tax_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="low", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    signals_payload: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
