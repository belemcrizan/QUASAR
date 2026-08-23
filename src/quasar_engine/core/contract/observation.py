"""Domain-neutral observation contract."""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Relation(BaseModel):
    """Optional known relationship attached to an observation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    relation_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    weight: float = Field(default=1.0, ge=0.0)


class Observation(BaseModel):
    """The single contract every domain adapter must produce.

    ``target_future`` is evaluation-only. The detection pipeline intentionally
    ignores it so that changing a label cannot change a prediction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    timestamp: datetime
    source_id: str = Field(min_length=1)
    entity_id: str | None = None
    features: dict[str, float] = Field(min_length=1)
    relations: tuple[Relation, ...] = ()
    context: dict[str, Any] = Field(default_factory=dict)
    target_future: int | None = Field(default=None, ge=0, le=1)

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("features")
    @classmethod
    def validate_features(cls, value: dict[str, float]) -> dict[str, float]:
        clean: dict[str, float] = {}
        for name, raw in value.items():
            if not name.strip():
                raise ValueError("feature names cannot be blank")
            number = float(raw)
            if not math.isfinite(number):
                raise ValueError(f"feature {name!r} must be finite")
            clean[name] = number
        return clean

    @property
    def observation_id(self) -> str:
        payload = f"{self.timestamp.isoformat()}|{self.source_id}|{self.entity_id or ''}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]

