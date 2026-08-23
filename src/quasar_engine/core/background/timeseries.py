"""A minimal seasonal-naive background for future time-series extensions."""

from __future__ import annotations

from collections import defaultdict, deque

from quasar_engine.core.background.base import BackgroundModel, BackgroundSnapshot
from quasar_engine.core.contract.observation import Observation


class SeasonalNaiveBackground(BackgroundModel):
    """Dependency-free baseline; ARIMA/Prophet adapters can implement the same interface."""

    def __init__(self, period: int = 7, min_history: int = 21) -> None:
        self.period = period
        self.min_history = min_history
        self._values: dict[str, dict[str, deque[float]]] = defaultdict(dict)

    def score(self, observation: Observation) -> BackgroundSnapshot:
        source = self._values.get(observation.source_id, {})
        residuals: dict[str, float] = {}
        centers: dict[str, float] = {}
        scales: dict[str, float] = {}
        counts: list[int] = []
        for name, current in observation.features.items():
            values = source.get(name)
            if not values:
                continue
            history = list(values)
            counts.append(len(history))
            center = history[-self.period] if len(history) >= self.period else history[-1]
            absolute_errors = [abs(b - a) for a, b in zip(history, history[1:], strict=False)]
            scale = max(sum(absolute_errors) / max(1, len(absolute_errors)), 1e-6)
            centers[name] = center
            scales[name] = scale
            residuals[name] = (current - center) / scale
        count = min(counts, default=0)
        return BackgroundSnapshot(residuals, centers, scales, count, count >= self.min_history)

    def update(self, observation: Observation) -> None:
        source = self._values[observation.source_id]
        maxlen = max(self.period * 4, self.min_history)
        for name, value in observation.features.items():
            if name not in source:
                source[name] = deque(maxlen=maxlen)
            source[name].append(float(value))

    def reset(self) -> None:
        self._values.clear()

