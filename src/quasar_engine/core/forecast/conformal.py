"""Split-conformal intervals for binary targets."""

from __future__ import annotations

import math

import numpy as np


class SplitConformalInterval:
    """Distribution-free interval around a probability using past residuals.

    For a binary target this interval can be wide. That is an honest expression
    of POC uncertainty, not a confidence interval for a causal effect.
    """

    def __init__(self, coverage: float = 0.90) -> None:
        if not 0.5 < coverage < 1.0:
            raise ValueError("coverage must be in (0.5, 1)")
        self.coverage = coverage
        self.quantile = 1.0

    def fit(self, probabilities: list[float], labels: list[int]) -> "SplitConformalInterval":
        if len(probabilities) != len(labels) or not probabilities:
            raise ValueError("non-empty probabilities and labels must have equal length")
        scores = np.abs(np.asarray(labels, dtype=float) - np.asarray(probabilities, dtype=float))
        n = len(scores)
        level = min(1.0, math.ceil((n + 1) * self.coverage) / n)
        try:
            self.quantile = float(np.quantile(scores, level, method="higher"))
        except TypeError:  # NumPy < 1.22 compatibility
            self.quantile = float(np.quantile(scores, level, interpolation="higher"))
        return self

    def interval(self, probability: float) -> tuple[float, float]:
        return max(0.0, probability - self.quantile), min(1.0, probability + self.quantile)

