"""Transparent score-to-probability forecast for the POC."""

from __future__ import annotations

import math

from quasar_engine.core.forecast.base import ProbabilisticForecaster


class LogisticEmergenceForecaster(ProbabilisticForecaster):
    """Map the detector threshold to probability 0.5 using a logistic curve."""

    def __init__(self, threshold: float, slope: float = 9.0) -> None:
        self.threshold = threshold
        self.slope = slope

    def predict_probability(self, score: float) -> float:
        logit = self.slope * (float(score) - self.threshold)
        if logit >= 0:
            return 1.0 / (1.0 + math.exp(-logit))
        exponential = math.exp(logit)
        return exponential / (1.0 + exponential)

