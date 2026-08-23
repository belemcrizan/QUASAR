"""Domain adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from typing import Any

from quasar_engine.core.contract.observation import Observation


class DomainAdapter(ABC):
    domain: str

    @abstractmethod
    def adapt(self, record: Mapping[str, Any]) -> Observation:
        raise NotImplementedError

    def adapt_many(self, records: Iterable[Mapping[str, Any]]) -> list[Observation]:
        return [self.adapt(record) for record in records]

