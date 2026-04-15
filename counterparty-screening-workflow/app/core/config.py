from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Counterparty Screening Workflow"
    app_version: str = "0.5.0"
    app_env: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./data/counterparty_risk.db"
    auto_migrate_on_startup: bool = False
    risk_high_threshold: int = 70
    risk_medium_threshold: int = 40
    max_risk_score: int = 100
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:8080"]
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("API prefix must start with '/'.")
        normalized = value.rstrip("/") or "/"
        return normalized

    @model_validator(mode="after")
    def validate_thresholds(self) -> "Settings":
        if self.risk_medium_threshold >= self.risk_high_threshold:
            raise ValueError("RISK_MEDIUM_THRESHOLD must be lower than RISK_HIGH_THRESHOLD.")
        if self.max_risk_score <= 0:
            raise ValueError("MAX_RISK_SCORE must be greater than zero.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
