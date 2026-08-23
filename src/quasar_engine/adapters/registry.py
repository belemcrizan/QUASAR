"""Registry for domain adapters."""

from __future__ import annotations

from collections.abc import Callable

from quasar_engine.adapters.base import DomainAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], DomainAdapter]] = {}

    def register(self, name: str, factory: Callable[[], DomainAdapter]) -> None:
        self._factories[name.strip().lower()] = factory

    def create(self, name: str) -> DomainAdapter:
        key = name.strip().lower()
        if key not in self._factories:
            raise KeyError(f"unknown adapter {name!r}; available: {', '.join(self.names())}")
        return self._factories[key]()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))


ADAPTERS = AdapterRegistry()

