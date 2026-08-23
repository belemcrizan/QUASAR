"""Histogram-based mutual information change."""

from __future__ import annotations

import numpy as np

from quasar_engine.core.dynamics.base import clip01


def mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 6) -> float:
    joint, _, _ = np.histogram2d(x, y, bins=bins)
    total = float(joint.sum())
    if total == 0:
        return 0.0
    pxy = joint / total
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = (pxy > 0) & (expected > 0)
    return float(np.sum(pxy[mask] * np.log2(pxy[mask] / expected[mask])))


def mutual_information_change(
    reference_x: np.ndarray,
    reference_y: np.ndarray,
    recent_x: np.ndarray,
    recent_y: np.ndarray,
    bins: int = 6,
) -> float:
    before = mutual_information(reference_x, reference_y, bins)
    after = mutual_information(recent_x, recent_y, bins)
    return clip01(abs(after - before) / max(np.log2(bins), 1.0))

