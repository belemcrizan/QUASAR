"""Small in-process counter collector."""

from __future__ import annotations

from collections import Counter


class Metrics:
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()

    def increment(self, name: str, amount: int = 1) -> None:
        self._counters[name] += amount

    def snapshot(self) -> dict[str, int]:
        return dict(self._counters)

