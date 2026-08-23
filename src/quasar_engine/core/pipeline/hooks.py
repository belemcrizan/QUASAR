"""Optional lifecycle hooks; all are no-ops by default."""

from __future__ import annotations

from typing import Protocol

from quasar_engine.core.contract.candidate import Candidate


class PipelineHook(Protocol):
    def on_candidate(self, candidate: Candidate) -> None: ...


class NullHook:
    def on_candidate(self, candidate: Candidate) -> None:
        del candidate

