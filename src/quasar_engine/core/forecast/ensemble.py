"""Probability ensemble utility."""

from __future__ import annotations


def weighted_probability(probabilities: list[float], weights: list[float] | None = None) -> float:
    if not probabilities:
        raise ValueError("at least one probability is required")
    if weights is None:
        weights = [1.0] * len(probabilities)
    if len(probabilities) != len(weights) or sum(weights) <= 0:
        raise ValueError("probabilities and positive weights must align")
    if any(not 0.0 <= value <= 1.0 for value in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    return sum(p * w for p, w in zip(probabilities, weights, strict=True)) / sum(weights)

