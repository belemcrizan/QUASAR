"""Registered synthetic experiments and temporal validation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from quasar_engine.adapters.astronomy import AstronomyAdapter, generate_synthetic_astronomy
from quasar_engine.adapters.fraud import FraudAdapter, generate_synthetic_fraud
from quasar_engine.core.forecast.calibration import make_calibrator
from quasar_engine.core.forecast.conformal import SplitConformalInterval
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.context import RunContext
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline
from quasar_engine.core.validation.baselines import (
    IsolationForestBaseline,
    change_point_probability,
    constant_base_rate_probability,
    residual_only_probability,
)
from quasar_engine.core.validation.comparator import compare
from quasar_engine.core.validation.metrics import (
    classification_metrics,
    empirical_coverage,
    lead_time_steps,
    probabilistic_metrics,
)
from quasar_engine.core.validation.temporal_cv import TemporalSplit
from quasar_engine.monitoring.profiler import ProfileResult, profile
from quasar_engine.reporting.markdown import render_run_report
from quasar_engine.storage.local import LocalArtifactStore


def make_observations(
    domain: str, points: int, seed: int, horizon: int
) -> list[Any]:
    if domain == "fraud":
        return FraudAdapter().adapt_many(generate_synthetic_fraud(points, seed, horizon))
    if domain == "astronomy":
        return AstronomyAdapter().adapt_many(generate_synthetic_astronomy(points, seed, horizon))
    raise ValueError(f"unsupported demo domain: {domain}")


def _metric_bundle(probabilities: list[float], labels: list[int], bins: int) -> dict[str, float]:
    return {
        **probabilistic_metrics(probabilities, labels, bins),
        **classification_metrics(probabilities, labels),
    }


def _calibrate_series(
    probabilities: list[float], labels: list[int], split: TemporalSplit, method: str
) -> tuple[list[float], dict[str, float | int | str]]:
    calibrator = make_calibrator(method).fit(
        probabilities[split.calibration], labels[split.calibration]
    )
    return calibrator.transform(probabilities), calibrator.parameters()


def _feature_matrix(output: Any) -> np.ndarray:
    names = sorted(
        set().union(*(item.observation.features.keys() for item in output.scored))
    )
    matrix = np.asarray(
        [[item.observation.features.get(name, np.nan) for name in names] for item in output.scored],
        dtype=float,
    )
    if not np.all(np.isfinite(matrix)):
        medians = np.nanmedian(matrix, axis=0)
        medians = np.where(np.isfinite(medians), medians, 0.0)
        rows, columns = np.where(~np.isfinite(matrix))
        matrix[rows, columns] = medians[columns]
    return matrix


def run_observations(
    observations: list[Any],
    domain: str,
    seed: int = 42,
    config: PipelineConfig | None = None,
    output_dir: str | Path | None = None,
    *,
    data_name: str = "custom",
    synthetic: bool = False,
) -> dict[str, Any]:
    config = config or PipelineConfig()
    points = len(observations)
    if points < 20:
        raise ValueError("an evaluation experiment requires at least 20 observations")
    if any(observation.target_future is None for observation in observations):
        raise ValueError("evaluation requires target_future on every observation")
    pipeline = DiscoveryPipeline(config)
    profile_result = ProfileResult()
    with profile(profile_result):
        output = pipeline.process(observations)

    if len(output.scored) < 20:
        raise RuntimeError("too few scored observations; increase points or reduce warm-up")

    split = TemporalSplit.create(
        len(output.scored),
        config.validation.calibration_fraction,
        config.validation.test_fraction,
    )
    raw = [item.forecast.probability for item in output.scored]
    labels = [int(item.observation.target_future or 0) for item in output.scored]
    event_now = [int(item.observation.context.get("event_now", 0)) for item in output.scored]

    calibration_method = config.validation.calibration_method
    calibrated_all, calibration_parameters = _calibrate_series(
        raw, labels, split, calibration_method
    )
    conformal = SplitConformalInterval(config.forecast.conformal_coverage).fit(
        calibrated_all[split.calibration], labels[split.calibration]
    )
    intervals = [conformal.interval(value) for value in calibrated_all]

    test_labels = labels[split.test]
    test_raw = raw[split.test]
    test_calibrated = calibrated_all[split.test]
    bins = config.validation.calibration_bins
    raw_metrics = _metric_bundle(test_raw, test_labels, bins)
    calibrated_metrics = _metric_bundle(test_calibrated, test_labels, bins)
    calibrated_metrics["coverage"] = empirical_coverage(intervals[split.test], test_labels)

    residual_baseline_raw = [
        residual_only_probability(item.emergence.metrics["residual"]) for item in output.scored
    ]
    change_baseline_raw = [
        change_point_probability(item.emergence.metrics["change_point"]) for item in output.scored
    ]
    residual_baseline_all, _ = _calibrate_series(
        residual_baseline_raw, labels, split, calibration_method
    )
    change_baseline_all, _ = _calibrate_series(
        change_baseline_raw, labels, split, calibration_method
    )
    feature_matrix = _feature_matrix(output)
    isolation_raw = IsolationForestBaseline(seed=seed).fit(
        feature_matrix[: split.calibration_start]
    ).score_samples(feature_matrix)
    isolation_all, _ = _calibrate_series(isolation_raw, labels, split, calibration_method)
    calibration_rate = sum(labels[split.calibration]) / len(labels[split.calibration])
    rate_baseline_all = [constant_base_rate_probability(calibration_rate)] * len(labels)
    baselines = {
        "residual_only": _metric_bundle(residual_baseline_all[split.test], test_labels, bins),
        "change_point_only": _metric_bundle(change_baseline_all[split.test], test_labels, bins),
        "isolation_forest": _metric_bundle(isolation_all[split.test], test_labels, bins),
        "constant_base_rate": _metric_bundle(rate_baseline_all[split.test], test_labels, bins),
    }

    target_semantics = sorted(
        {
            str(item.observation.context.get("target_semantics", "future event within horizon"))
            for item in output.scored
        }
    )
    lead_time_applicable = not any(
        "current-row classification" in value for value in target_semantics
    )
    lead = (
        lead_time_steps(calibrated_all, event_now, config.forecast.horizon_steps)
        if lead_time_applicable
        else None
    )
    throughput = len(observations) / max(profile_result.elapsed_seconds, 1e-9)
    best_baseline_brier = min(item["brier"] for item in baselines.values())
    comparisons = {
        name: [asdict(row) for row in compare(calibrated_metrics, metrics)]
        for name, metrics in baselines.items()
    }
    context = RunContext.create(config, seed, domain, points)

    result: dict[str, Any] = {
        "project": "QUASAR",
        "expansion": "Quantified Uncertainty Analysis for Signals, Anomalies, and Regimes",
        "status": "evidence_generated_not_scientific_conclusion",
        "domain": domain,
        "data": {
            "synthetic": synthetic,
            "name": data_name,
            "points": points,
            "scored_after_warmup": len(output.scored),
            "positive_labels": sum(labels),
            "event_steps": sum(event_now),
            "target_semantics": target_semantics,
        },
        "validation": {
            "protocol": "chronological warmup -> calibration -> held-out test",
            "calibration_start": split.calibration_start,
            "test_start": split.test_start,
            "calibration_method": calibration_method,
            "calibration_parameters": calibration_parameters,
            "forecast_method": config.forecast.method,
            "conformal_quantile": conformal.quantile,
            "requested_coverage": conformal.coverage,
            "lead_time_applicable": lead_time_applicable,
        },
        "metrics": {
            "raw_test": raw_metrics,
            "calibrated_test": calibrated_metrics,
            "baselines_test": baselines,
            "lead_time_steps": lead,
        },
        "comparison": comparisons,
        "candidates": len(output.candidates),
        "go_no_go_indicators": {
            "beats_best_registered_baseline_on_brier": calibrated_metrics["brier"] < best_baseline_brier,
            "calibration_measured": True,
            "held_out_test_used": True,
            "causal_claim_made": False,
            "core_unchanged_between_domains": True,
        },
        "performance": {
            "elapsed_seconds": profile_result.elapsed_seconds,
            "peak_memory_mb": profile_result.peak_memory_mb,
            "observations_per_second": throughput,
        },
        "run": asdict(context),
    }

    if output_dir is not None:
        store = LocalArtifactStore(output_dir)
        prediction_rows = []
        for index, item in enumerate(output.scored):
            prediction_rows.append(
                {
                    "observation_id": item.observation.observation_id,
                    "timestamp": item.observation.timestamp,
                    "raw_probability": raw[index],
                    "calibrated_probability": calibrated_all[index],
                    "interval": {"lower": intervals[index][0], "upper": intervals[index][1]},
                    "label_revealed_for_evaluation": labels[index],
                    "event_now": event_now[index],
                    "emergence_score": item.emergence.score,
                    "evidence_metrics": item.emergence.metrics,
                    "candidate_id": item.candidate.candidate_id if item.candidate else None,
                    "partition": (
                        "test"
                        if index >= split.test_start
                        else "calibration"
                        if index >= split.calibration_start
                        else "background"
                    ),
                }
            )
        store.write_json("results.json", result)
        store.write_json("run_manifest.json", asdict(context))
        store.write_jsonl("predictions.jsonl", prediction_rows)
        store.write_jsonl("candidates.jsonl", list(output.candidates))
        store.write_jsonl("hypotheses.jsonl", list(output.hypotheses))
        store.write_text("report.md", render_run_report(result))

    return result


def run_domain(
    domain: str,
    points: int = 360,
    seed: int = 42,
    config: PipelineConfig | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    config = config or PipelineConfig()
    observations = make_observations(domain, points, seed, config.forecast.horizon_steps)
    return run_observations(
        observations,
        domain,
        seed,
        config,
        output_dir,
        data_name=f"synthetic_{domain}",
        synthetic=True,
    )


def run_demo(
    domains: list[str],
    points: int,
    seed: int,
    config: PipelineConfig,
    output_dir: str | Path,
) -> dict[str, Any]:
    root = Path(output_dir)
    results = {
        domain: run_domain(domain, points, seed, config, root / domain) for domain in domains
    }
    summary = {
        "project": "QUASAR",
        "domains": results,
        "shared_core": "The identical DiscoveryPipeline and PipelineConfig were used in every domain.",
        "scope_note": "Synthetic POC results do not establish scientific novelty or production readiness.",
    }
    LocalArtifactStore(root).write_json("summary.json", summary)
    return summary
