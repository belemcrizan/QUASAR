"""Reproducible synthetic fraud/surveillance stream."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np


def generate_synthetic_fraud(
    points: int = 360, seed: int = 42, horizon: int = 4
) -> list[dict[str, Any]]:
    if points < 100:
        raise ValueError("synthetic experiment requires at least 100 points")
    rng = np.random.default_rng(seed)
    centers = [int(points * fraction) for fraction in (0.34, 0.63, 0.86)]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    records: list[dict[str, Any]] = []

    for index in range(points):
        precursor = 0.0
        event_now = 0
        for center in centers:
            distance = center - index
            if 0 <= distance <= horizon + 2:
                precursor = max(precursor, (horizon + 3 - distance) / (horizon + 3))
            if center <= index < center + 3:
                event_now = 1
                precursor = max(precursor, 1.15)

        weekly = np.sin(2.0 * np.pi * index / 24.0)
        record = {
            "timestamp": start + timedelta(hours=index),
            "source_id": "payments_stream",
            "entity_id": f"account_{index % 17:02d}",
            "amount_log": 4.4 + 0.14 * weekly + rng.normal(0.0, 0.28) + 0.62 * precursor,
            "velocity": 2.2 + 0.10 * weekly + rng.normal(0.0, 0.48) + 1.10 * precursor,
            "counterparty_risk": np.clip(
                0.22 + rng.normal(0.0, 0.07) + 0.24 * precursor, 0.0, 1.0
            ),
            "network_density": np.clip(
                0.12 + rng.normal(0.0, 0.035) + 0.13 * precursor, 0.0, 1.0
            ),
            "relations": [
                {
                    "relation_type": "transacts_with",
                    "target_id": f"counterparty_{index % 9:02d}",
                    "weight": float(0.4 + 0.4 * min(precursor, 1.0)),
                }
            ],
            "synthetic": True,
            "event_now": event_now,
            "target_future": int(
                event_now or any(index < center <= index + horizon for center in centers)
            ),
        }
        records.append(record)
    return records

