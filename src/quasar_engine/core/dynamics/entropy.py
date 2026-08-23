"""Shannon entropy and normalized entropy change."""

from __future__ import annotations

import numpy as np

from quasar_engine.core.dynamics.base import DynamicsMetric, clip01


def shannon_entropy(values: np.ndarray, edges: np.ndarray) -> float:
    counts, _ = np.histogram(values, bins=edges)
    probabilities = counts.astype(float)
    total = float(probabilities.sum())
    if total == 0:
        return 0.0
    probabilities /= total
    probabilities = probabilities[probabilities > 0]
    return float(-np.sum(probabilities * np.log2(probabilities)))


class EntropyChange(DynamicsMetric):
    def __init__(self, bins: int = 8) -> None:
        self.bins = max(2, bins)

    def compare(self, reference: np.ndarray, recent: np.ndarray) -> float:
        combined = np.concatenate([reference, recent])
        low, high = float(np.min(combined)), float(np.max(combined))
        if high - low < 1e-12:
            return 0.0
        edges = np.linspace(low, high, self.bins + 1)
        delta = abs(shannon_entropy(recent, edges) - shannon_entropy(reference, edges))
        return clip01(delta / np.log2(self.bins))

