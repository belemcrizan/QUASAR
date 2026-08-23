"""Copy this adapter when adding a real domain."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from quasar_engine.adapters.base import DomainAdapter
from quasar_engine.core.contract.observation import Observation


class TemplateAdapter(DomainAdapter):
    domain = "replace_me"

    def adapt(self, record: Mapping[str, Any]) -> Observation:
        return Observation(
            timestamp=record["timestamp"],
            source_id=str(record["source_id"]),
            entity_id=str(record["entity_id"]) if record.get("entity_id") is not None else None,
            features={str(name): float(value) for name, value in record["features"].items()},
            context={"domain": self.domain},
            target_future=record.get("target_future"),
        )

