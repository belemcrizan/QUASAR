"""Run metadata for reproducibility."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

from quasar_engine import __version__
from quasar_engine.core.pipeline.config import PipelineConfig


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str
    started_at: str
    seed: int
    domain: str
    points: int
    package_version: str
    python_version: str
    platform: str
    config_sha256: str

    @classmethod
    def create(cls, config: PipelineConfig, seed: int, domain: str, points: int) -> "RunContext":
        config_json = json.dumps(config.model_dump(mode="json"), sort_keys=True)
        digest = hashlib.sha256(config_json.encode("utf-8")).hexdigest()
        run_id = hashlib.sha256(f"{domain}|{seed}|{points}|{digest}".encode()).hexdigest()[:16]
        return cls(
            run_id=run_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            seed=seed,
            domain=domain,
            points=points,
            package_version=__version__,
            python_version=sys.version.split()[0],
            platform=platform.platform(),
            config_sha256=digest,
        )

