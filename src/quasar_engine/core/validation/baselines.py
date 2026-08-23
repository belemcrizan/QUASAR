"""Transparent baseline probability mappings."""

from __future__ import annotations

import math


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def residual_only_probability(residual_score: float) -> float:
    return _sigmoid(9.0 * (residual_score - 0.42))


def change_point_probability(change_score: float) -> float:
    return _sigmoid(10.0 * (change_score - 0.36))


def constant_base_rate_probability(rate: float) -> float:
    return min(max(float(rate), 1e-6), 1.0 - 1e-6)

