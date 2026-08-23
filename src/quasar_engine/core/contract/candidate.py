"""Candidate and evidence contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric: str = Field(min_length=1)
    raw_value: float
    normalized_value: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0)
    direction: Literal["increase", "decrease", "shift", "unknown"] = "shift"
    description: str = Field(min_length=1)


class Candidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str = Field(min_length=1)
    observation_id: str = Field(min_length=1)
    timestamp: datetime
    source_id: str
    entity_id: str | None = None
    domain: str
    score: float = Field(ge=0.0, le=1.0)
    evidence: tuple[Evidence, ...]
    status: Literal["candidate", "validated", "weakened", "rejected"] = "candidate"

