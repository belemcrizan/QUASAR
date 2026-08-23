"""Adapter from telescope-like observations to the common contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from quasar_engine.adapters.base import DomainAdapter
from quasar_engine.adapters.registry import ADAPTERS
from quasar_engine.core.contract.observation import Observation


class AstronomyAdapter(DomainAdapter):
    domain = "astronomy"
    feature_names = ("flux", "color_index", "spectral_width", "local_background")

    def adapt(self, record: Mapping[str, Any]) -> Observation:
        missing = [name for name in ("timestamp", *self.feature_names) if name not in record]
        if missing:
            raise ValueError(f"astronomy record missing fields: {', '.join(missing)}")
        return Observation(
            timestamp=record["timestamp"],
            source_id=str(record.get("source_id", "telescope_A")),
            entity_id=str(record.get("entity_id", "sky_patch_unknown")),
            features={name: float(record[name]) for name in self.feature_names},
            context={
                "domain": self.domain,
                "synthetic": bool(record.get("synthetic", False)),
                "event_now": int(record.get("event_now", 0)),
                "description": "emerging transient in a telescope-like time series",
            },
            target_future=record.get("target_future"),
        )


ADAPTERS.register("astronomy", AstronomyAdapter)

