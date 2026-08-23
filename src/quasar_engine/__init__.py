"""Public API for QUASAR Discovery Engine."""

from quasar_engine.core.contract.candidate import Candidate, Evidence
from quasar_engine.core.contract.forecast import Forecast
from quasar_engine.core.contract.hypothesis import Hypothesis
from quasar_engine.core.contract.observation import Observation, Relation
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.orchestrator import DiscoveryPipeline, PipelineOutput

__all__ = [
    "Candidate",
    "DiscoveryPipeline",
    "Evidence",
    "Forecast",
    "Hypothesis",
    "Observation",
    "PipelineConfig",
    "PipelineOutput",
    "Relation",
]

__version__ = "0.1.0"

