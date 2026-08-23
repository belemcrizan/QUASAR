"""Small plugin registry for background models."""

from __future__ import annotations

from collections.abc import Callable

from quasar_engine.core.background.base import BackgroundModel


class BackgroundRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., BackgroundModel]] = {}

    def register(self, name: str, factory: Callable[..., BackgroundModel]) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("background name cannot be blank")
        self._factories[key] = factory

    def create(self, name: str, **kwargs: object) -> BackgroundModel:
        key = name.strip().lower()
        if key not in self._factories:
            available = ", ".join(sorted(self._factories)) or "none"
            raise KeyError(f"unknown background {name!r}; available: {available}")
        return self._factories[key](**kwargs)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))


BACKGROUNDS = BackgroundRegistry()

