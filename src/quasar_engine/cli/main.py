"""Command-line interface for local use and reproducible research studies."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from quasar_engine import __version__
from quasar_engine.adapters.astronomy import load_nasa_lightcurve_csv
from quasar_engine.adapters.fraud import load_ieee_cis_transactions
from quasar_engine.core.contract.observation import Observation
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline
from quasar_engine.experiment import run_demo, run_observations
from quasar_engine.monitoring.logger import configure_logging
from quasar_engine.research import (
    run_ablation_study,
    run_calibration_study,
    run_multiseed,
    run_scalability_study,
)
from quasar_engine.storage.local import LocalArtifactStore


def _add_model_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--threshold", type=float, help="override detector threshold")
    parser.add_argument("--horizon", type=int, help="override forecast horizon in steps")
    parser.add_argument(
        "--calibration-method", choices=["temperature", "platt", "isotonic"]
    )
    parser.add_argument("--forecast-method", choices=["logistic", "ensemble"])


def _add_synthetic_options(
    parser: argparse.ArgumentParser, default_output: str, include_domain_all: bool = True
) -> None:
    choices = ["fraud", "astronomy", "all"] if include_domain_all else ["fraud", "astronomy"]
    parser.add_argument("--domain", choices=choices, default="all" if include_domain_all else "fraud")
    parser.add_argument("--points", type=int, default=360)
    parser.add_argument("--seed", type=int, default=int(os.getenv("QUASAR_SEED", "42")))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(default_output))
    _add_model_options(parser)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quasar",
        description="QUASAR: weak-signal discovery and temporal falsification POC",
    )
    parser.add_argument("--version", action="version", version=f"QUASAR {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="run reproducible synthetic experiments")
    _add_synthetic_options(demo, os.getenv("QUASAR_OUTPUT_DIR", "runs/demo"))

    run = subparsers.add_parser("run", help="run the core on Observation-contract JSONL")
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, default=Path("runs/custom"))
    run.add_argument("--config", type=Path)
    _add_model_options(run)

    evaluate = subparsers.add_parser(
        "evaluate-data", help="evaluate labeled Observation JSONL with temporal holdout"
    )
    evaluate.add_argument("--input", type=Path, required=True)
    evaluate.add_argument("--domain", required=True)
    evaluate.add_argument("--data-name", default="custom_labeled_jsonl")
    evaluate.add_argument("--seed", type=int, default=42)
    evaluate.add_argument("--output-dir", type=Path, default=Path("runs/real-data"))
    evaluate.add_argument("--config", type=Path)
    _add_model_options(evaluate)

    benchmark = subparsers.add_parser(
        "benchmark", help="run repeated seeds and report variance plus 95 percent confidence intervals"
    )
    _add_synthetic_options(benchmark, "runs/multiseed")
    benchmark.add_argument("--seeds", type=int, default=30, help="number of consecutive seeds")
    benchmark.add_argument("--seed-start", type=int, default=0)

    ablate = subparsers.add_parser("ablate", help="run registered evidence ablations")
    _add_synthetic_options(ablate, "runs/ablation")

    calibrate = subparsers.add_parser(
        "calibrate", help="compare temperature, Platt, and isotonic calibration"
    )
    _add_synthetic_options(calibrate, "runs/calibration")
    calibrate.add_argument("--methods", default="temperature,platt,isotonic")

    scale = subparsers.add_parser("scale", help="run opt-in local scalability benchmarks")
    _add_synthetic_options(scale, "runs/scalability", include_domain_all=False)
    scale.add_argument("--sizes", default="1000,10000")
    scale.add_argument("--repeats", type=int, default=3)
    scale.add_argument("--confirm-large", action="store_true")

    prepare = subparsers.add_parser(
        "prepare-data", help="convert a supported local dataset CSV to Observation JSONL"
    )
    prepare.add_argument("--dataset", choices=["ieee-cis", "nasa-lightcurve"], required=True)
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--max-rows", type=int)
    prepare.add_argument("--curve-id")

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


def _configured(args: argparse.Namespace) -> PipelineConfig:
    config = _load_config(getattr(args, "config", None))
    detector_updates: dict[str, Any] = {}
    forecast_updates: dict[str, Any] = {}
    validation_updates: dict[str, Any] = {}
    if getattr(args, "threshold", None) is not None:
        detector_updates["threshold"] = args.threshold
    if getattr(args, "horizon", None) is not None:
        forecast_updates["horizon_steps"] = args.horizon
    if getattr(args, "forecast_method", None) is not None:
        forecast_updates["method"] = args.forecast_method
    if getattr(args, "calibration_method", None) is not None:
        validation_updates["calibration_method"] = args.calibration_method
    updates: dict[str, Any] = {}
    if detector_updates:
        updates["detector"] = config.detector.model_copy(update=detector_updates)
    if forecast_updates:
        updates["forecast"] = config.forecast.model_copy(update=forecast_updates)
    if validation_updates:
        updates["validation"] = config.validation.model_copy(update=validation_updates)
    return config.model_copy(update=updates)


def _domains(value: str) -> list[str]:
    return ["fraud", "astronomy"] if value == "all" else [value]


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
    print("Evidence only; this is not a production or causal conclusion.\n")
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
    output = DiscoveryPipeline(_configured(args)).process(observations)
    store = LocalArtifactStore(args.output_dir)
    store.write_jsonl("candidates.jsonl", list(output.candidates))
    store.write_jsonl("hypotheses.jsonl", list(output.hypotheses))
    store.write_jsonl("forecasts.jsonl", [item.forecast for item in output.scored])
    print(
        f"Validated {len(observations)} observations; scored {len(output.scored)}; "
        f"generated {len(output.candidates)} candidates."
    )
    print(f"Artifacts: {args.output_dir.resolve()}")


def _prepare_data(args: argparse.Namespace) -> None:
    if args.dataset == "ieee-cis":
        observations = load_ieee_cis_transactions(args.input, args.max_rows)
    else:
        observations = load_nasa_lightcurve_csv(args.input, args.max_rows, args.curve_id)
    LocalArtifactStore(args.output.parent).write_jsonl(args.output.name, observations)
    labeled = sum(observation.target_future is not None for observation in observations)
    print(f"Prepared {len(observations)} observations ({labeled} labeled): {args.output.resolve()}")


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = _parser().parse_args(argv)
    try:
        if args.command == "demo":
            summary = run_demo(
                _domains(args.domain), args.points, args.seed, _configured(args), args.output_dir
            )
            _print_demo_summary(summary, args.output_dir)
        elif args.command == "run":
            _run_custom(args)
        elif args.command == "evaluate-data":
            observations = _read_jsonl(args.input)
            result = run_observations(
                observations,
                args.domain,
                args.seed,
                _configured(args),
                args.output_dir,
                data_name=args.data_name,
                synthetic=False,
            )
            _print_demo_summary({"domains": {args.domain: result}}, args.output_dir)
        elif args.command == "benchmark":
            seeds = list(range(args.seed_start, args.seed_start + args.seeds))
            report = run_multiseed(
                _domains(args.domain), seeds, args.points, _configured(args), args.output_dir
            )
            print(f"Completed {report['seed_count']} seeds. Report: {args.output_dir.resolve()}")
        elif args.command == "ablate":
            run_ablation_study(
                _domains(args.domain), args.points, args.seed, _configured(args), args.output_dir
            )
            print(f"Ablation report: {args.output_dir.resolve()}")
        elif args.command == "calibrate":
            methods = [value.strip() for value in args.methods.split(",") if value.strip()]
            run_calibration_study(
                _domains(args.domain), methods, args.points, args.seed, _configured(args), args.output_dir
            )
            print(f"Calibration report: {args.output_dir.resolve()}")
        elif args.command == "scale":
            sizes = [int(value.strip()) for value in args.sizes.split(",") if value.strip()]
            run_scalability_study(
                args.domain,
                sizes,
                args.repeats,
                args.seed,
                _configured(args),
                args.output_dir,
                args.confirm_large,
            )
            print(f"Scalability report: {args.output_dir.resolve()}")
        elif args.command == "prepare-data":
            _prepare_data(args)
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
