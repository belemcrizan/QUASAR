"""Regime-change evidence without an HMM dependency."""

from __future__ import annotations

import numpy as np

from quasar_engine.core.dynamics.base import DynamicsMetric, clip01


class VarianceRegimeShift(DynamicsMetric):
    """Detect changes in variance; an HMM can replace it through the same interface."""

    def compare(self, reference: np.ndarray, recent: np.ndarray) -> float:
        var_ref = float(np.var(reference)) + 1e-8
        var_recent = float(np.var(recent)) + 1e-8
        log_ratio = abs(float(np.log(var_recent / var_ref)))
        return clip01(log_ratio / 3.0)

