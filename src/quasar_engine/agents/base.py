"""Governed contract for future investigative agents."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InvestigationPacket(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str
    hypothesis: str
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]
    testable_prediction: str
    rejection_criterion: str
    source_references: tuple[str, ...] = ()
    may_promote_discovery: bool = Field(default=False)

