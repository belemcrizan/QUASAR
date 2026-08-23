"""Command-line interface for local use."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from quasar_engine import __version__
from quasar_engine.core.contract.observation import Observation
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline
from quasar_engine.experiment import run_demo
from quasar_engine.monitoring.logger import configure_logging
from quasar_engine.storage.local import LocalArtifactStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quasar",
        description="QUASAR: weak-signal discovery and temporal falsification POC",
    )
    parser.add_argument("--version", action="version", version=f"QUASAR {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="run reproducible synthetic experiments")
    demo.add_argument("--domain", choices=["fraud", "astronomy", "all"], default="all")
    demo.add_argument("--points", type=int, default=360)
    demo.add_argument("--seed", type=int, default=int(os.getenv("QUASAR_SEED", "42")))
    demo.add_argument("--config", type=Path)
    demo.add_argument(
        "--output-dir", type=Path, default=Path(os.getenv("QUASAR_OUTPUT_DIR", "runs/demo"))
    )

    run = subparsers.add_parser("run", help="run the core on Observation-contract JSONL")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, default=Path("runs/custom"))
    run.add_argument("--config", type=Path)

    validate = subparsers.add_parser("validate-data", help="validate Observation JSONL")
    validate.add_argument("--input", type=Path, required=True)

    show = subparsers.add_parser("show-config", help="print resolved configuration")
    show.add_argument("--config", type=Path)

    serve = subparsers.add_parser("serve", help="start the optional local REST API")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def _load_config(path: Path | None) -> PipelineConfig:
    return PipelineConfig.from_yaml(path) if path else PipelineConfig()


def _read_jsonl(path: Path) -> list[Observation]:
    observations: list[Observation] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                observations.append(Observation.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValidationError) as exc:
                raise ValueError(f"invalid observation at line {line_number}: {exc}") from exc
    if not observations:
        raise ValueError("input contains no observations")
    return observations


def _print_demo_summary(summary: dict[str, Any], output_dir: Path) -> None:
    print("\nQUASAR POC completed")
    print("Synthetic evidence only; this is not a production or causal conclusion.\n")
    for domain, result in summary["domains"].items():
        metrics = result["metrics"]["calibrated_test"]
        print(
            f"- {domain}: candidates={result['candidates']}, "
            f"AUPRC={metrics['auprc']:.3f}, Brier={metrics['brier']:.3f}, "
            f"ECE={metrics['ece']:.3f}, coverage={metrics['coverage']:.3f}"
        )
    print(f"\nArtifacts: {output_dir.resolve()}")


def _run_custom(args: argparse.Namespace) -> None:
    observations = _read_jsonl(args.input)
    output = DiscoveryPipeline(_load_config(args.config)).process(observations)
    store = LocalArtifactStore(args.output_dir)
    store.write_jsonl("candidates.jsonl", list(output.candidates))
    store.write_jsonl("hypotheses.jsonl", list(output.hypotheses))
    store.write_jsonl("forecasts.jsonl", [item.forecast for item in output.scored])
    print(
        f"Validated {len(observations)} observations; scored {len(output.scored)}; "
        f"generated {len(output.candidates)} candidates."
    )
    print(f"Artifacts: {args.output_dir.resolve()}")


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = _parser().parse_args(argv)
    try:
        if args.command == "demo":
            config = _load_config(args.config)
            domains = ["fraud", "astronomy"] if args.domain == "all" else [args.domain]
            summary = run_demo(domains, args.points, args.seed, config, args.output_dir)
            _print_demo_summary(summary, args.output_dir)
        elif args.command == "run":
            _run_custom(args)
        elif args.command == "validate-data":
            observations = _read_jsonl(args.input)
            print(f"OK: {len(observations)} observations satisfy the contract.")
        elif args.command == "show-config":
            print(json.dumps(_load_config(args.config).model_dump(), indent=2, sort_keys=True))
        elif args.command == "serve":
            try:
                import uvicorn
            except ImportError as exc:
                raise RuntimeError(
                    'API dependencies are optional. Install with: python -m pip install -e ".[api]"'
                ) from exc
            uvicorn.run("quasar_engine.api.app:create_app", factory=True, host=args.host, port=args.port)
    except (OSError, RuntimeError, ValueError, KeyError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

