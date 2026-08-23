"""Deterministic Markdown reports for human review and international sharing."""

from __future__ import annotations

import math
from typing import Any


def _number(value: Any, digits: int = 4) -> str:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return f"{float(value):.{digits}f}"
    return "n/a"


def render_run_report(result: dict[str, Any]) -> str:
    metrics = result["metrics"]["calibrated_test"]
    baseline_rows = "\n".join(
        f"| {name} | {_number(values['brier'])} | {_number(values['ece'])} | "
        f"{_number(values['auprc'])} | {_number(values['auroc'])} |"
        for name, values in result["metrics"]["baselines_test"].items()
    )
    indicators = "\n".join(
        f"- `{name}`: **{str(value).lower()}**"
        for name, value in result["go_no_go_indicators"].items()
    )
    return f"""# QUASAR experiment report

**Domain:** {result['domain']}  
**Status:** `{result['status']}`  
**Seed:** {result['run']['seed']}  
**Calibration:** {result['validation']['calibration_method']}  
**Forecast:** {result['validation']['forecast_method']}

> This report records POC evidence. It does not establish causality, scientific novelty, production readiness, or general superiority.

## Held-out test metrics

| Metric | Value |
|---|---:|
| Brier score | {_number(metrics['brier'])} |
| Log loss | {_number(metrics['log_loss'])} |
| ECE | {_number(metrics['ece'])} |
| AUPRC | {_number(metrics['auprc'])} |
| AUROC | {_number(metrics['auroc'])} |
| Precision | {_number(metrics['precision'])} |
| Recall | {_number(metrics['recall'])} |
| FPR | {_number(metrics['fpr'])} |
| Empirical coverage | {_number(metrics['coverage'])} |
| Lead time, steps | {_number(result['metrics']['lead_time_steps'], 2)} |

## Registered baselines

| Baseline | Brier | ECE | AUPRC | AUROC |
|---|---:|---:|---:|---:|
{baseline_rows}

## GO/NO-GO indicators

{indicators}

## Compute profile

- Elapsed seconds: {_number(result['performance']['elapsed_seconds'], 3)}
- Peak memory MB: {_number(result['performance']['peak_memory_mb'], 2)}
- Observations/second: {_number(result['performance']['observations_per_second'], 1)}

## Reproducibility

- Run ID: `{result['run']['run_id']}`
- Configuration SHA-256: `{result['run']['config_sha256']}`
- Python: `{result['run']['python_version']}`
- Platform: `{result['run']['platform']}`
"""


def render_multiseed_report(report: dict[str, Any]) -> str:
    lines = [
        "# QUASAR multi-seed report",
        "",
        f"Seeds: {report['seed_count']} (`{report['seeds'][0]}` to `{report['seeds'][-1]}`)",
        "",
        "> Confidence intervals summarize repeated synthetic POC runs; they are not a substitute for real-data external validation.",
        "",
    ]
    for domain, domain_result in report["domains"].items():
        lines.extend(
            [
                f"## {domain}",
                "",
                "| Metric | Mean | Std | 95% CI low | 95% CI high |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for metric, stats in domain_result["metrics"].items():
            lines.append(
                f"| {metric} | {_number(stats['mean'])} | {_number(stats['std'])} | "
                f"{_number(stats['ci95_low'])} | {_number(stats['ci95_high'])} |"
            )
        lines.extend(["", f"GO rate on Brier gate: {_number(domain_result['go_rate'], 3)}", ""])
    return "\n".join(lines)


def render_ablation_report(report: dict[str, Any]) -> str:
    lines = [
        "# QUASAR ablation report",
        "",
        "> Each variant uses the same seed, observations, temporal split, and validation protocol.",
        "",
    ]
    for domain, variants in report["domains"].items():
        lines.extend(
            [
                f"## {domain}",
                "",
                "| Variant | Brier | ECE | AUPRC | AUROC | Candidates |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for name, result in variants.items():
            metrics = result["metrics"]["calibrated_test"]
            lines.append(
                f"| {name} | {_number(metrics['brier'])} | {_number(metrics['ece'])} | "
                f"{_number(metrics['auprc'])} | {_number(metrics['auroc'])} | {result['candidates']} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_calibration_report(report: dict[str, Any]) -> str:
    lines = [
        "# QUASAR calibration study",
        "",
        "> Methods use the same observations, seed, temporal split, and held-out test. Selection must be made on a separate protocol; the test set must not be reused for tuning.",
        "",
    ]
    for domain, methods in report["domains"].items():
        lines.extend(
            [
                f"## {domain}",
                "",
                "| Method | Brier | Log loss | ECE | Coverage | AUPRC |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for name, result in methods.items():
            metrics = result["metrics"]["calibrated_test"]
            lines.append(
                f"| {name} | {_number(metrics['brier'])} | {_number(metrics['log_loss'])} | "
                f"{_number(metrics['ece'])} | {_number(metrics['coverage'])} | "
                f"{_number(metrics['auprc'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_scalability_report(report: dict[str, Any]) -> str:
    lines = [
        "# QUASAR scalability report",
        "",
        f"Domain: `{report['domain']}`; repeats per size: `{report['repeats']}`.",
        "",
        "| Observations | p50 seconds | p95 seconds | Peak memory MB | Throughput obs/s |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in report["sizes"]:
        lines.append(
            f"| {row['observations']} | {_number(row['elapsed_p50'], 3)} | "
            f"{_number(row['elapsed_p95'], 3)} | {_number(row['peak_memory_mb'], 2)} | "
            f"{_number(row['throughput_observations_per_second'], 1)} |"
        )
    lines.extend(
        [
            "",
            "> The one-million-observation run is opt-in. Measure it on controlled hardware and record the environment before making scale claims.",
        ]
    )
    return "\n".join(lines)
