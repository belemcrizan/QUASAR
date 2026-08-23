"""Probabilistic forecast contract."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Forecast(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    observation_id: str
    candidate_id: str | None = None
    probability: float = Field(ge=0.0, le=1.0)
    lower: float = Field(ge=0.0, le=1.0)
    upper: float = Field(ge=0.0, le=1.0)
    horizon_steps: int = Field(ge=1)
    method: str
    calibrated: bool = False

    @model_validator(mode="after")
    def interval_contains_probability(self) -> "Forecast":
        if not self.lower <= self.probability <= self.upper:
            raise ValueError("forecast interval must contain probability")
        return self
