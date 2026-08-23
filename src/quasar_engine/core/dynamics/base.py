"""Shared numerical helpers for information dynamics."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


def clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


class DynamicsMetric(ABC):
    @abstractmethod
    def compare(self, reference: np.ndarray, recent: np.ndarray) -> float:
        """Return a normalized change score in [0, 1]."""
        raise NotImplementedError

