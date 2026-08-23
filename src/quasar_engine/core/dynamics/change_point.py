"""Fast two-window change-point proxy."""

from __future__ import annotations

import numpy as np

from quasar_engine.core.dynamics.base import DynamicsMetric, clip01


class StandardizedMeanShift(DynamicsMetric):
    """Effect-size detector used as a cheap candidate generator before PELT/Bayesian methods."""

    def compare(self, reference: np.ndarray, recent: np.ndarray) -> float:
        pooled = np.concatenate([reference, recent])
        scale = max(float(np.std(pooled)), 1e-6)
        effect = abs(float(np.mean(recent) - np.mean(reference))) / scale
        return clip01(effect / 3.0)

