"""Run leave-one-evidence-out ablations on fixed synthetic streams."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.experiment import run_domain
from quasar_engine.storage.local import LocalArtifactStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=["fraud", "astronomy", "all"], default="all")
    parser.add_argument("--points", type=int, default=360)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("runs/ablation"))
    args = parser.parse_args()
    domains = ["fraud", "astronomy"] if args.domain == "all" else [args.domain]
    base = PipelineConfig()
    report: dict[str, object] = {}
    for domain in domains:
        domain_rows: dict[str, object] = {}
        domain_rows["full"] = run_domain(domain, args.points, args.seed, base)
        for omitted in base.detector.weights:
            weights = dict(base.detector.weights)
            weights[omitted] = 0.0
            config = base.model_copy(
                update={"detector": base.detector.model_copy(update={"weights": weights})}
            )
            domain_rows[f"without_{omitted}"] = run_domain(
                domain, args.points, args.seed, config
            )
        report[domain] = domain_rows
    LocalArtifactStore(args.output_dir).write_json("ablation.json", report)
    print(json.dumps({domain: list(rows) for domain, rows in report.items()}, indent=2))


if __name__ == "__main__":
    main()

