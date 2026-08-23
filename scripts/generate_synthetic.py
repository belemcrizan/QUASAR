"""Generate Observation-contract JSONL for local inspection or custom runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from quasar_engine.experiment import make_observations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=["fraud", "astronomy"], required=True)
    parser.add_argument("--points", type=int, default=360)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--horizon", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    observations = make_observations(args.domain, args.points, args.seed, args.horizon)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for observation in observations:
            handle.write(json.dumps(observation.model_dump(mode="json"), sort_keys=True) + "\n")
    print(f"Wrote {len(observations)} observations to {args.output}")


if __name__ == "__main__":
    main()

