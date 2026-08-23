"""Forecast model interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProbabilisticForecaster(ABC):
    @abstractmethod
    def predict_probability(self, score: float) -> float:
        raise NotImplementedError

