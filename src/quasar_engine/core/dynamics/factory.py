"""Configuration-driven information dynamics engine."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from quasar_engine.core.contract.observation import Observation
from quasar_engine.core.dynamics.change_point import StandardizedMeanShift
from quasar_engine.core.dynamics.divergence import JensenShannonChange
from quasar_engine.core.dynamics.entropy import EntropyChange
from quasar_engine.core.dynamics.mutual_info import mutual_information_change
from quasar_engine.core.dynamics.regime import VarianceRegimeShift


@dataclass(frozen=True, slots=True)
class DynamicalEvidence:
    entropy_change: float = 0.0
    mutual_info_change: float = 0.0
    js_divergence: float = 0.0
    change_point: float = 0.0
    regime_change: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "entropy_change": self.entropy_change,
            "mutual_info_change": self.mutual_info_change,
            "js_divergence": self.js_divergence,
            "change_point": self.change_point,
            "regime_change": self.regime_change,
        }


class InformationDynamicsEngine:
    def __init__(self, recent_window: int = 12, bins: int = 8) -> None:
        if recent_window < 4:
            raise ValueError("recent_window must be at least 4")
        self.recent_window = recent_window
        self.entropy = EntropyChange(bins)
        self.divergence = JensenShannonChange(bins)
        self.change_point = StandardizedMeanShift()
        self.regime = VarianceRegimeShift()
        self.bins = bins

    def evaluate(
        self, history: list[Observation], current: Observation
    ) -> DynamicalEvidence:
        width = self.recent_window
        if len(history) < 2 * width - 1:
            return DynamicalEvidence()

        feature_names = sorted(current.features)
        per_feature: dict[str, dict[str, float]] = {}
        arrays: dict[str, tuple[np.ndarray, np.ndarray]] = {}

        for name in feature_names:
            values = [item.features[name] for item in history if name in item.features]
            if len(values) < 2 * width - 1:
                continue
            reference = np.asarray(values[-(2 * width - 1) : -width + 1], dtype=float)
            recent = np.asarray(values[-width + 1 :] + [current.features[name]], dtype=float)
            if len(reference) != width or len(recent) != width:
                continue
            arrays[name] = (reference, recent)
            per_feature[name] = {
                "entropy": self.entropy.compare(reference, recent),
                "js": self.divergence.compare(reference, recent),
                "change": self.change_point.compare(reference, recent),
                "regime": self.regime.compare(reference, recent),
            }

        if not per_feature:
            return DynamicalEvidence()

        def mean(metric: str) -> float:
            return float(np.mean([values[metric] for values in per_feature.values()]))

        mutual_changes: list[float] = []
        paired = list(arrays.items())[:4]
        for index, (_, first) in enumerate(paired):
            for _, second in paired[index + 1 :]:
                mutual_changes.append(
                    mutual_information_change(
                        first[0], second[0], first[1], second[1], bins=min(self.bins, 6)
                    )
                )

        return DynamicalEvidence(
            entropy_change=mean("entropy"),
            mutual_info_change=float(np.mean(mutual_changes)) if mutual_changes else 0.0,
            js_divergence=mean("js"),
            change_point=mean("change"),
            regime_change=mean("regime"),
        )
