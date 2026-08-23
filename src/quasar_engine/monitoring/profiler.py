"""Local wall-clock and peak-memory profiler."""

from __future__ import annotations

import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator


@dataclass(slots=True)
class ProfileResult:
    elapsed_seconds: float = 0.0
    peak_memory_mb: float = 0.0


@contextmanager
def profile(result: ProfileResult) -> Iterator[None]:
    tracemalloc.start()
    started = time.perf_counter()
    try:
        yield
    finally:
        result.elapsed_seconds = time.perf_counter() - started
        _, peak = tracemalloc.get_traced_memory()
        result.peak_memory_mb = peak / (1024 * 1024)
        tracemalloc.stop()

