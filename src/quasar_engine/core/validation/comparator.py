"""Structured model comparison."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Comparison:
    metric: str
    candidate: float
    baseline: float
    delta: float
    better: bool


def compare(
    candidate_metrics: dict[str, float], baseline_metrics: dict[str, float]
) -> list[Comparison]:
    lower_is_better = {"brier", "log_loss", "ece", "fpr"}
    rows: list[Comparison] = []
    for metric in sorted(candidate_metrics.keys() & baseline_metrics.keys()):
        candidate = candidate_metrics[metric]
        baseline = baseline_metrics[metric]
        if candidate != candidate or baseline != baseline:  # NaN
            continue
        better = candidate < baseline if metric in lower_is_better else candidate > baseline
        rows.append(Comparison(metric, candidate, baseline, candidate - baseline, better))
    return rows
