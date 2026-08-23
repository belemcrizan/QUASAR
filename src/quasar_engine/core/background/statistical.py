"""Incremental rolling statistical background."""

from __future__ import annotations

from collections import defaultdict, deque

import numpy as np

from quasar_engine.core.background.base import BackgroundModel, BackgroundSnapshot
from quasar_engine.core.background.registry import BACKGROUNDS
from quasar_engine.core.contract.observation import Observation


class StatisticalBackground(BackgroundModel):
    """Robust median/MAD or classic mean/std background per source and feature."""

    def __init__(self, window: int = 48, min_history: int = 24, robust: bool = True) -> None:
        if min_history < 3 or window < min_history:
            raise ValueError("require window >= min_history >= 3")
        self.window = window
        self.min_history = min_history
        self.robust = robust
        self._values: dict[str, dict[str, deque[float]]] = defaultdict(dict)

    def score(self, observation: Observation) -> BackgroundSnapshot:
        source = self._values.get(observation.source_id, {})
        centers: dict[str, float] = {}
        scales: dict[str, float] = {}
        residuals: dict[str, float] = {}
        counts: list[int] = []

        for name, current in observation.features.items():
            values = source.get(name)
            if not values:
                continue
            array = np.asarray(values, dtype=float)
            counts.append(len(array))
            if self.robust:
                center = float(np.median(array))
                mad = float(np.median(np.abs(array - center)))
                scale = 1.4826 * mad
                if scale < 1e-9:
                    scale = float(np.std(array))
            else:
                center = float(np.mean(array))
                scale = float(np.std(array))
            scale = max(scale, 1e-6)
            centers[name] = center
            scales[name] = scale
            residuals[name] = (float(current) - center) / scale

        sample_count = min(counts, default=0)
        return BackgroundSnapshot(
            residuals=residuals,
            centers=centers,
            scales=scales,
            sample_count=sample_count,
            ready=bool(residuals) and sample_count >= self.min_history,
        )

    def update(self, observation: Observation) -> None:
        source = self._values[observation.source_id]
        for name, value in observation.features.items():
            if name not in source:
                source[name] = deque(maxlen=self.window)
            source[name].append(float(value))

    def reset(self) -> None:
        self._values.clear()


BACKGROUNDS.register("statistical", StatisticalBackground)

