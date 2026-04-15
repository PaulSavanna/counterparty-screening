from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Severity = Literal["low", "medium", "high"]


class CheckCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    country: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Company name must contain at least two characters.")
        return normalized

    @field_validator("tax_id")
    @classmethod
    def normalize_tax_id(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip().upper().replace(" ", "")
        if not normalized:
            return None
        if not normalized.replace("-", "").isalnum():
            raise ValueError("Tax ID must contain only letters, numbers, or dashes.")
        return normalized

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if len(normalized) != 2 or not normalized.isalpha():
            raise ValueError("Country must be a two-letter ISO-like code.")
        return normalized


class RiskSignal(BaseModel):
    source: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=3, max_length=120)
    score: int = Field(ge=0, le=100)
    details: str = Field(min_length=3, max_length=500)


class CheckComputation(BaseModel):
    company_name: str
    tax_id: str | None
    country: str | None
    risk_score: float = Field(ge=0)
    severity: Severity
    summary: str
    signals: list[RiskSignal]


class CheckResponse(CheckComputation):
    id: int
    created_at: datetime


class CheckListResponse(BaseModel):
    items: list[CheckResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
