"""Validation interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Validator(ABC):
    @abstractmethod
    def evaluate(self, probabilities: list[float], labels: list[int]) -> dict[str, float]:
        raise NotImplementedError

