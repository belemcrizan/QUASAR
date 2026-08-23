"""Leakage-safe split calibration."""

from __future__ import annotations

import numpy as np


def _clip(probabilities: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1.0 - 1e-6)


class TemperatureCalibrator:
    """Fit a scalar temperature by minimizing log-loss on a past calibration slice."""

    def __init__(self) -> None:
        self.temperature = 1.0

    def fit(self, probabilities: list[float], labels: list[int]) -> "TemperatureCalibrator":
        if len(probabilities) != len(labels) or not probabilities:
            raise ValueError("non-empty probabilities and labels must have equal length")
        p = _clip(np.asarray(probabilities))
        y = np.asarray(labels, dtype=float)
        logits = np.log(p / (1.0 - p))
        candidates = np.geomspace(0.25, 6.0, 160)
        losses: list[float] = []
        for temperature in candidates:
            adjusted = 1.0 / (1.0 + np.exp(-logits / temperature))
            adjusted = _clip(adjusted)
            losses.append(float(-np.mean(y * np.log(adjusted) + (1.0 - y) * np.log(1.0 - adjusted))))
        self.temperature = float(candidates[int(np.argmin(losses))])
        return self

    def transform(self, probabilities: list[float]) -> list[float]:
        if not probabilities:
            return []
        p = _clip(np.asarray(probabilities))
        logits = np.log(p / (1.0 - p))
        adjusted = 1.0 / (1.0 + np.exp(-logits / self.temperature))
        return [float(value) for value in adjusted]

