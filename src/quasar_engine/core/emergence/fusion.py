"""Transparent weighted fusion for emergence evidence."""

from __future__ import annotations

from quasar_engine.core.emergence.base import EvidenceFusion


class WeightedEvidenceFusion(EvidenceFusion):
    def __init__(self, weights: dict[str, float], synergy_threshold: float = 0.30) -> None:
        if not weights or sum(weights.values()) <= 0:
            raise ValueError("at least one positive evidence weight is required")
        if any(weight < 0 for weight in weights.values()):
            raise ValueError("evidence weights cannot be negative")
        self.weights = weights
        self.synergy_threshold = synergy_threshold

    def combine(self, metrics: dict[str, float]) -> float:
        total_weight = sum(self.weights.values())
        base = sum(
            self.weights[name] * min(max(float(metrics.get(name, 0.0)), 0.0), 1.0)
            for name in self.weights
        ) / total_weight
        # Convergent independent evidence is more informative than one large metric.
        active = sum(float(metrics.get(name, 0.0)) >= self.synergy_threshold for name in self.weights)
        boost = min(0.16, max(0, active - 2) * 0.04)
        return min(1.0, base + boost * (1.0 - base))

