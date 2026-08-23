"""Interfaces for expected-behaviour models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from quasar_engine.core.contract.observation import Observation


@dataclass(frozen=True, slots=True)
class BackgroundSnapshot:
    residuals: dict[str, float]
    centers: dict[str, float]
    scales: dict[str, float]
    sample_count: int
    ready: bool


class BackgroundModel(ABC):
    """A side-effect-free score followed by an explicit update."""

    @abstractmethod
    def score(self, observation: Observation) -> BackgroundSnapshot:
        raise NotImplementedError

    @abstractmethod
    def update(self, observation: Observation) -> None:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

