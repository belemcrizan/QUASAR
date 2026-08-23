"""Combine background snapshots without coupling to a domain."""

from __future__ import annotations

from quasar_engine.core.background.base import BackgroundModel, BackgroundSnapshot
from quasar_engine.core.contract.observation import Observation


class BackgroundEnsemble(BackgroundModel):
    def __init__(self, models: list[BackgroundModel]) -> None:
        if not models:
            raise ValueError("at least one background model is required")
        self.models = models

    def score(self, observation: Observation) -> BackgroundSnapshot:
        snapshots = [model.score(observation) for model in self.models]
        names = set().union(*(snapshot.residuals for snapshot in snapshots))
        residuals = {
            name: sum(snapshot.residuals.get(name, 0.0) for snapshot in snapshots) / len(snapshots)
            for name in names
        }
        centers = snapshots[0].centers
        scales = snapshots[0].scales
        return BackgroundSnapshot(
            residuals=residuals,
            centers=centers,
            scales=scales,
            sample_count=min(snapshot.sample_count for snapshot in snapshots),
            ready=all(snapshot.ready for snapshot in snapshots),
        )

    def update(self, observation: Observation) -> None:
        for model in self.models:
            model.update(observation)

    def reset(self) -> None:
        for model in self.models:
            model.reset()
