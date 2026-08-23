"""Artifact storage interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ArtifactStore(ABC):
    @abstractmethod
    def write_json(self, relative_path: str, payload: Any) -> Path:
        raise NotImplementedError

    @abstractmethod
    def write_jsonl(self, relative_path: str, rows: list[Any]) -> Path:
        raise NotImplementedError

