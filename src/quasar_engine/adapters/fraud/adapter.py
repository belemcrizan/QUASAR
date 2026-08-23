"""Adapter from fraud/surveillance records to the common contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from quasar_engine.adapters.base import DomainAdapter
from quasar_engine.adapters.registry import ADAPTERS
from quasar_engine.core.contract.observation import Observation, Relation


class FraudAdapter(DomainAdapter):
    domain = "fraud"
    feature_names = ("amount_log", "velocity", "counterparty_risk", "network_density")

    def adapt(self, record: Mapping[str, Any]) -> Observation:
        missing = [name for name in ("timestamp", *self.feature_names) if name not in record]
        if missing:
            raise ValueError(f"fraud record missing fields: {', '.join(missing)}")
        relations = tuple(
            Relation.model_validate(item) for item in record.get("relations", ())
        )
        return Observation(
            timestamp=record["timestamp"],
            source_id=str(record.get("source_id", "fraud_stream")),
            entity_id=str(record.get("entity_id", "account_unknown")),
            features={name: float(record[name]) for name in self.feature_names},
            relations=relations,
            context={
                "domain": self.domain,
                "synthetic": bool(record.get("synthetic", False)),
                "event_now": int(record.get("event_now", 0)),
                "description": "joint behaviour shift in a transaction stream",
            },
            target_future=record.get("target_future"),
        )


ADAPTERS.register("fraud", FraudAdapter)

