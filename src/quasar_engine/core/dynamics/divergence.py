"""Distribution divergence metrics."""

from __future__ import annotations

import numpy as np

from quasar_engine.core.dynamics.base import DynamicsMetric, clip01


def _probabilities(values: np.ndarray, edges: np.ndarray, epsilon: float = 1e-9) -> np.ndarray:
    counts, _ = np.histogram(values, bins=edges)
    probabilities = counts.astype(float) + epsilon
    return probabilities / probabilities.sum()


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.sum(p * np.log2(p / q)))


def js_divergence(reference: np.ndarray, recent: np.ndarray, bins: int = 8) -> float:
    combined = np.concatenate([reference, recent])
    low, high = float(np.min(combined)), float(np.max(combined))
    if high - low < 1e-12:
        return 0.0
    edges = np.linspace(low, high, bins + 1)
    p = _probabilities(reference, edges)
    q = _probabilities(recent, edges)
    midpoint = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, midpoint) + 0.5 * kl_divergence(q, midpoint)


def wasserstein_1d(reference: np.ndarray, recent: np.ndarray) -> float:
    """Quantile approximation of 1-Wasserstein distance without SciPy."""
    size = max(len(reference), len(recent), 8)
    quantiles = np.linspace(0.0, 1.0, size)
    return float(np.mean(np.abs(np.quantile(reference, quantiles) - np.quantile(recent, quantiles))))


class JensenShannonChange(DynamicsMetric):
    def __init__(self, bins: int = 8) -> None:
        self.bins = bins

    def compare(self, reference: np.ndarray, recent: np.ndarray) -> float:
        # JS divergence with log2 is bounded by 1. Square root improves separation
        # in small samples and is itself a metric.
        return clip01(np.sqrt(max(js_divergence(reference, recent, self.bins), 0.0)))

