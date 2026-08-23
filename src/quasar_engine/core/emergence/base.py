"""Interfaces for evidence fusion."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EvidenceFusion(ABC):
    @abstractmethod
    def combine(self, metrics: dict[str, float]) -> float:
        raise NotImplementedError

