"""Simple Beta-Bernoulli base-rate estimator."""

from __future__ import annotations


class BetaRateEstimator:
    def __init__(self, alpha: float = 1.0, beta: float = 1.0) -> None:
        if alpha <= 0 or beta <= 0:
            raise ValueError("alpha and beta must be positive")
        self.alpha = alpha
        self.beta = beta

    def update(self, label: int) -> None:
        if label not in (0, 1):
            raise ValueError("label must be 0 or 1")
        self.alpha += label
        self.beta += 1 - label

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

