"""Stable candidate ranking."""

from __future__ import annotations

from quasar_engine.core.contract.candidate import Candidate


def rank(candidates: list[Candidate]) -> list[Candidate]:
    return sorted(candidates, key=lambda item: (-item.score, item.timestamp, item.candidate_id))

