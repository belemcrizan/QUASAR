"""Candidate pruning utilities."""

from __future__ import annotations

from quasar_engine.core.contract.candidate import Candidate


def prune(candidates: list[Candidate], minimum_score: float) -> list[Candidate]:
    return [candidate for candidate in candidates if candidate.score >= minimum_score]

