"""Dependency factories kept separate for future cloud injection."""

from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline


def new_pipeline() -> DiscoveryPipeline:
    # One pipeline per request keeps the POC deterministic and avoids shared mutable state.
    return DiscoveryPipeline(PipelineConfig())

