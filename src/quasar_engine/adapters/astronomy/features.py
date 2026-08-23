"""Reproducible synthetic astronomical transient stream."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np


def generate_synthetic_astronomy(
    points: int = 360, seed: int = 42, horizon: int = 4
) -> list[dict[str, Any]]:
    if points < 100:
        raise ValueError("synthetic experiment requires at least 100 points")
    rng = np.random.default_rng(seed + 10_000)
    centers = [int(points * fraction) for fraction in (0.37, 0.68, 0.88)]
    start = datetime(2026, 2, 1, tzinfo=timezone.utc)
    records: list[dict[str, Any]] = []

    for index in range(points):
        precursor = 0.0
        event_now = 0
        for center in centers:
            distance = center - index
            if 0 <= distance <= horizon + 3:
                precursor = max(precursor, (horizon + 4 - distance) / (horizon + 4))
            if center <= index < center + 3:
                event_now = 1
                precursor = max(precursor, 1.20)

        cadence = np.sin(2.0 * np.pi * index / 31.0)
        records.append(
            {
                "timestamp": start + timedelta(minutes=30 * index),
                "source_id": "telescope_A",
                "entity_id": "sky_patch_Q17",
                "flux": 1.00 + 0.018 * cadence + rng.normal(0.0, 0.030) + 0.085 * precursor,
                "color_index": 0.52 + rng.normal(0.0, 0.025) - 0.060 * precursor,
                "spectral_width": 0.31 + rng.normal(0.0, 0.022) + 0.060 * precursor,
                "local_background": 0.09 + rng.normal(0.0, 0.012) + 0.026 * precursor,
                "synthetic": True,
                "event_now": event_now,
                "target_future": int(
                    event_now or any(index < center <= index + horizon for center in centers)
                ),
            }
        )
    return records

