"""Leakage-safe probability calibrators fitted on a chronological calibration slice."""

from __future__ import annotations

import numpy as np


class CalibrationModel:
    """Small common interface used by the experiment runner."""

    name = "base"

    def fit(self, probabilities: list[float], labels: list[int]) -> "CalibrationModel":
        raise NotImplementedError

    def transform(self, probabilities: list[float]) -> list[float]:
        raise NotImplementedError

    def parameters(self) -> dict[str, float | int | str]:
        return {}


def _clip(probabilities: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(probabilities, dtype=float), 1e-6, 1.0 - 1e-6)


class TemperatureCalibrator(CalibrationModel):
    """Fit a scalar temperature by minimizing log-loss on a past calibration slice."""

    name = "temperature"

    def __init__(self) -> None:
        self.temperature = 1.0

    def fit(self, probabilities: list[float], labels: list[int]) -> "TemperatureCalibrator":
        if len(probabilities) != len(labels) or not probabilities:
            raise ValueError("non-empty probabilities and labels must have equal length")
        p = _clip(np.asarray(probabilities))
        y = np.asarray(labels, dtype=float)
        logits = np.log(p / (1.0 - p))
        candidates = np.geomspace(0.05, 10.0, 240)
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

    def parameters(self) -> dict[str, float]:
        return {"temperature": self.temperature}


class PlattCalibrator(CalibrationModel):
    """Fit ``sigmoid(a * logit(p) + b)`` with damped Newton updates."""

    name = "platt"

    def __init__(self, l2: float = 1e-4, max_iter: int = 100) -> None:
        self.l2 = l2
        self.max_iter = max_iter
        self.a = 1.0
        self.b = 0.0

    def fit(self, probabilities: list[float], labels: list[int]) -> "PlattCalibrator":
        if len(probabilities) != len(labels) or not probabilities:
            raise ValueError("non-empty probabilities and labels must have equal length")
        p = _clip(np.asarray(probabilities))
        y = np.asarray(labels, dtype=float)
        x = np.log(p / (1.0 - p))

        for _ in range(self.max_iter):
            z = np.clip(self.a * x + self.b, -30.0, 30.0)
            fitted = 1.0 / (1.0 + np.exp(-z))
            residual = fitted - y
            weight = np.maximum(fitted * (1.0 - fitted), 1e-8)
            gradient = np.asarray(
                [np.sum(residual * x) + self.l2 * self.a, np.sum(residual) + self.l2 * self.b]
            )
            hessian = np.asarray(
                [
                    [np.sum(weight * x * x) + self.l2, np.sum(weight * x)],
                    [np.sum(weight * x), np.sum(weight) + self.l2],
                ]
            )
            try:
                update = np.linalg.solve(hessian, gradient)
            except np.linalg.LinAlgError:
                break
            update = np.clip(update, -1.0, 1.0)
            self.a -= float(update[0])
            self.b -= float(update[1])
            if float(np.linalg.norm(update)) < 1e-7:
                break
        return self

    def transform(self, probabilities: list[float]) -> list[float]:
        if not probabilities:
            return []
        p = _clip(np.asarray(probabilities))
        logits = np.log(p / (1.0 - p))
        adjusted = 1.0 / (1.0 + np.exp(-np.clip(self.a * logits + self.b, -30.0, 30.0)))
        return [float(value) for value in adjusted]

    def parameters(self) -> dict[str, float]:
        return {"a": self.a, "b": self.b, "l2": self.l2}


class IsotonicCalibrator(CalibrationModel):
    """Monotonic non-parametric calibration using the pool-adjacent-violators algorithm."""

    name = "isotonic"

    def __init__(self) -> None:
        self._upper_bounds = np.asarray([1.0], dtype=float)
        self._values = np.asarray([0.5], dtype=float)

    def fit(self, probabilities: list[float], labels: list[int]) -> "IsotonicCalibrator":
        if len(probabilities) != len(labels) or not probabilities:
            raise ValueError("non-empty probabilities and labels must have equal length")
        order = np.argsort(np.asarray(probabilities), kind="stable")
        x = np.asarray(probabilities, dtype=float)[order]
        y = np.asarray(labels, dtype=float)[order]
        blocks: list[dict[str, float | int]] = [
            {"start": index, "end": index, "weight": 1.0, "value": float(value)}
            for index, value in enumerate(y)
        ]
        index = 0
        while index < len(blocks) - 1:
            if float(blocks[index]["value"]) <= float(blocks[index + 1]["value"]):
                index += 1
                continue
            left, right = blocks[index], blocks[index + 1]
            weight = float(left["weight"]) + float(right["weight"])
            value = (
                float(left["value"]) * float(left["weight"])
                + float(right["value"]) * float(right["weight"])
            ) / weight
            blocks[index : index + 2] = [
                {
                    "start": int(left["start"]),
                    "end": int(right["end"]),
                    "weight": weight,
                    "value": value,
                }
            ]
            index = max(0, index - 1)

        self._upper_bounds = np.asarray([x[int(block["end"])] for block in blocks], dtype=float)
        self._values = np.asarray([float(block["value"]) for block in blocks], dtype=float)
        return self

    def transform(self, probabilities: list[float]) -> list[float]:
        if not probabilities:
            return []
        values = np.asarray(probabilities, dtype=float)
        indices = np.searchsorted(self._upper_bounds, values, side="left")
        indices = np.clip(indices, 0, len(self._values) - 1)
        return [float(value) for value in self._values[indices]]

    def parameters(self) -> dict[str, int]:
        return {"blocks": int(len(self._values))}


def make_calibrator(name: str) -> CalibrationModel:
    factories: dict[str, type[CalibrationModel]] = {
        "temperature": TemperatureCalibrator,
        "platt": PlattCalibrator,
        "isotonic": IsotonicCalibrator,
    }
    key = name.strip().lower()
    if key not in factories:
        raise ValueError(f"unknown calibration method {name!r}; choose {', '.join(factories)}")
    return factories[key]()
