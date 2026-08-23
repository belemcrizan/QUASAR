"""Reproducible research studies layered on top of the unchanged discovery core."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline
from quasar_engine.experiment import make_observations, run_domain
from quasar_engine.monitoring.profiler import ProfileResult, profile
from quasar_engine.reporting.markdown import (
    render_ablation_report,
    render_calibration_report,
    render_multiseed_report,
    render_scalability_report,
)
from quasar_engine.storage.local import LocalArtifactStore


REPORTED_METRICS = (
    "brier",
    "log_loss",
    "ece",
    "auprc",
    "auroc",
    "precision",
    "recall",
    "fpr",
    "coverage",
)


def _confidence_summary(
    values: list[float], bounds: tuple[float, float] | None = None
) -> dict[str, float]:
    finite = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    if len(finite) == 0:
        return {"mean": math.nan, "std": math.nan, "ci95_low": math.nan, "ci95_high": math.nan}
    mean = float(np.mean(finite))
    std = float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0
    margin = 1.96 * std / math.sqrt(len(finite))
    low, high = mean - margin, mean + margin
    if bounds is not None:
        low = max(bounds[0], low)
        high = min(bounds[1], high)
    return {"mean": mean, "std": std, "ci95_low": low, "ci95_high": high}


def run_multiseed(
    domains: list[str],
    seeds: list[int],
    points: int,
    config: PipelineConfig,
    output_dir: str | Path,
) -> dict[str, Any]:
    if len(seeds) < 2:
        raise ValueError("multi-seed analysis requires at least two seeds")
    rows: list[dict[str, Any]] = []
    domains_report: dict[str, Any] = {}
    for domain in domains:
        results = [run_domain(domain, points, seed, config) for seed in seeds]
        for seed, result in zip(seeds, results, strict=True):
            rows.append(
                {
                    "domain": domain,
                    "seed": seed,
                    "metrics": result["metrics"]["calibrated_test"],
                    "lead_time_steps": result["metrics"]["lead_time_steps"],
                    "candidates": result["candidates"],
                    "go": result["go_no_go_indicators"][
                        "beats_best_registered_baseline_on_brier"
                    ],
                    "run_id": result["run"]["run_id"],
                }
            )
        metric_summary = {
            metric: _confidence_summary(
                [float(result["metrics"]["calibrated_test"][metric]) for result in results],
                (0.0, 1.0) if metric != "log_loss" else None,
            )
            for metric in REPORTED_METRICS
        }
        metric_summary["lead_time_steps"] = _confidence_summary(
            [float(result["metrics"]["lead_time_steps"]) for result in results]
        )
        metric_summary["candidates"] = _confidence_summary(
            [float(result["candidates"]) for result in results]
        )
        domains_report[domain] = {
            "metrics": metric_summary,
            "go_rate": sum(
                result["go_no_go_indicators"]["beats_best_registered_baseline_on_brier"]
                for result in results
            )
            / len(results),
        }

    report = {
        "project": "QUASAR",
        "study": "multi_seed",
        "seed_count": len(seeds),
        "seeds": seeds,
        "points_per_seed": points,
        "domains": domains_report,
        "scope_note": "Synthetic repeated-run evidence; not real-world external validation.",
    }
    store = LocalArtifactStore(output_dir)
    store.write_json("multiseed.json", report)
    store.write_jsonl("runs.jsonl", rows)
    store.write_text("report.md", render_multiseed_report(report))
    return report


def run_ablation_study(
    domains: list[str],
    points: int,
    seed: int,
    config: PipelineConfig,
    output_dir: str | Path,
) -> dict[str, Any]:
    variants: dict[str, dict[str, float]] = {"full": dict(config.detector.weights)}
    residual_only = {name: 0.0 for name in config.detector.weights}
    residual_only["residual"] = 1.0
    variants["residual_only_no_fusion"] = residual_only
    for omitted in (
        "entropy_change",
        "mutual_info_change",
        "js_divergence",
        "change_point",
        "regime_change",
    ):
        weights = dict(config.detector.weights)
        weights[omitted] = 0.0
        variants[f"without_{omitted}"] = weights

    domain_results: dict[str, Any] = {}
    for domain in domains:
        domain_results[domain] = {}
        for name, weights in variants.items():
            variant_config = config.model_copy(
                update={"detector": config.detector.model_copy(update={"weights": weights})}
            )
            domain_results[domain][name] = run_domain(domain, points, seed, variant_config)

    report = {
        "project": "QUASAR",
        "study": "ablation",
        "seed": seed,
        "points": points,
        "domains": domain_results,
    }
    store = LocalArtifactStore(output_dir)
    store.write_json("ablation.json", report)
    store.write_text("report.md", render_ablation_report(report))
    return report


def run_calibration_study(
    domains: list[str],
    methods: list[str],
    points: int,
    seed: int,
    config: PipelineConfig,
    output_dir: str | Path,
) -> dict[str, Any]:
    if not methods:
        raise ValueError("at least one calibration method is required")
    domain_results: dict[str, Any] = {}
    for domain in domains:
        domain_results[domain] = {}
        for method in methods:
            method_config = config.model_copy(
                update={
                    "validation": config.validation.model_copy(
                        update={"calibration_method": method}
                    )
                }
            )
            domain_results[domain][method] = run_domain(
                domain, points, seed, method_config
            )
    report = {
        "project": "QUASAR",
        "study": "calibration",
        "seed": seed,
        "points": points,
        "methods": methods,
        "domains": domain_results,
        "selection_warning": "Do not select a method on the held-out test and report the same test as unbiased.",
    }
    store = LocalArtifactStore(output_dir)
    store.write_json("calibration.json", report)
    store.write_text("report.md", render_calibration_report(report))
    return report


def run_scalability_study(
    domain: str,
    sizes: list[int],
    repeats: int,
    seed: int,
    config: PipelineConfig,
    output_dir: str | Path,
    confirm_large: bool = False,
) -> dict[str, Any]:
    if repeats < 1:
        raise ValueError("repeats must be at least one")
    if not sizes or any(size < 100 for size in sizes):
        raise ValueError("all benchmark sizes must be at least 100")
    if max(sizes) > 100_000 and not confirm_large:
        raise ValueError("sizes above 100,000 require --confirm-large because they may exhaust memory")
    rows: list[dict[str, Any]] = []
    for size in sizes:
        elapsed: list[float] = []
        memory: list[float] = []
        for repeat in range(repeats):
            result = ProfileResult()
            with profile(result):
                observations = make_observations(
                    domain, size, seed + repeat, config.forecast.horizon_steps
                )
                DiscoveryPipeline(config).process(observations)
            elapsed.append(result.elapsed_seconds)
            memory.append(result.peak_memory_mb)
        p50 = float(np.quantile(elapsed, 0.50))
        p95 = float(np.quantile(elapsed, 0.95))
        rows.append(
            {
                "observations": size,
                "elapsed_seconds": elapsed,
                "elapsed_p50": p50,
                "elapsed_p95": p95,
                "peak_memory_mb": max(memory),
                "throughput_observations_per_second": size / max(p50, 1e-9),
            }
        )
    report = {
        "project": "QUASAR",
        "study": "scalability",
        "domain": domain,
        "repeats": repeats,
        "sizes": rows,
        "scope_note": "Local core benchmark; no cloud cost or distributed-systems claim.",
    }
    store = LocalArtifactStore(output_dir)
    store.write_json("scalability.json", report)
    store.write_text("report.md", render_scalability_report(report))
    return report
