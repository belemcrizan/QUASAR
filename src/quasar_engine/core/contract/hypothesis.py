"""Explicitly testable structural hypothesis."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str
    statement: str = Field(min_length=1)
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...] = ()
    testable_prediction: str
    rejection_criterion: str
    causal_claim: bool = False

