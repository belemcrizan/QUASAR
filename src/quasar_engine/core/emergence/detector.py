"""Turn background residuals and dynamics into a candidate score."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from quasar_engine.core.background.base import BackgroundSnapshot
from quasar_engine.core.contract.candidate import Evidence
from quasar_engine.core.dynamics.factory import DynamicalEvidence
from quasar_engine.core.emergence.fusion import WeightedEvidenceFusion


@dataclass(frozen=True, slots=True)
class EmergenceScore:
    score: float
    metrics: dict[str, float]
    evidence: tuple[Evidence, ...]
    is_candidate: bool


DESCRIPTIONS = {
    "residual": "Combined deviation from the expected behaviour learned only from prior data.",
    "entropy_change": "Change in the distribution's information content between adjacent windows.",
    "mutual_info_change": "Change in statistical dependence between feature pairs.",
    "js_divergence": "Distance between the current and reference distributions.",
    "change_point": "Standardized shift between the means of adjacent windows.",
    "regime_change": "Change in variance consistent with a possible regime transition.",
}


class EmergenceDetector:
    def __init__(self, weights: dict[str, float], threshold: float = 0.34) -> None:
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be in (0, 1)")
        self.threshold = threshold
        self.fusion = WeightedEvidenceFusion(weights)
        self.weights = weights

    @staticmethod
    def residual_score(snapshot: BackgroundSnapshot) -> float:
        if not snapshot.residuals:
            return 0.0
        absolute = sorted((abs(value) for value in snapshot.residuals.values()), reverse=True)
        # Use up to the three strongest weak signals. Normal noise (z~1) stays low,
        # while several moderate deviations can accumulate.
        z_mean = float(np.mean(absolute[:3]))
        return float(np.clip(1.0 - np.exp(-max(0.0, z_mean - 0.35) / 2.5), 0.0, 1.0))

    def evaluate(
        self, snapshot: BackgroundSnapshot, dynamics: DynamicalEvidence
    ) -> EmergenceScore:
        metrics = {"residual": self.residual_score(snapshot), **dynamics.as_dict()}
        score = self.fusion.combine(metrics)
        evidence = tuple(
            Evidence(
                metric=name,
                raw_value=(
                    float(np.mean([abs(value) for value in snapshot.residuals.values()]))
                    if name == "residual" and snapshot.residuals
                    else value
                ),
                normalized_value=value,
                weight=self.weights.get(name, 0.0),
                direction="shift",
                description=DESCRIPTIONS[name],
            )
            for name, value in sorted(metrics.items(), key=lambda item: item[1], reverse=True)
            if name in self.weights and self.weights[name] > 0
        )
        return EmergenceScore(score, metrics, evidence, score >= self.threshold)

