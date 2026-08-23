"""Local, atomic, human-readable artifact storage."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from quasar_engine.storage.base import ArtifactStore


def _json_default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "__dict__"):
        return value.__dict__
    raise TypeError(f"cannot serialize {type(value).__name__}")


class LocalArtifactStore(ArtifactStore):
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _target(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        if self.root not in target.parents and target != self.root:
            raise ValueError("artifact path must stay inside the store root")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def _atomic_text(self, target: Path, text: str) -> Path:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", dir=target.parent, text=True
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, target)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
        return target

    def write_json(self, relative_path: str, payload: Any) -> Path:
        target = self._target(relative_path)
        text = json.dumps(payload, default=_json_default, indent=2, sort_keys=True, ensure_ascii=False)
        return self._atomic_text(target, text + "\n")

    def write_text(self, relative_path: str, text: str) -> Path:
        target = self._target(relative_path)
        return self._atomic_text(target, text.rstrip() + "\n")

    def write_jsonl(self, relative_path: str, rows: list[Any]) -> Path:
        target = self._target(relative_path)
        text = "\n".join(
            json.dumps(row, default=_json_default, sort_keys=True, ensure_ascii=False) for row in rows
        )
        return self._atomic_text(target, text + ("\n" if rows else ""))
