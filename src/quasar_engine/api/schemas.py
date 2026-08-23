"""Optional REST API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from quasar_engine.core.contract.candidate import Candidate
from quasar_engine.core.contract.forecast import Forecast
from quasar_engine.core.contract.hypothesis import Hypothesis
from quasar_engine.core.contract.observation import Observation


class DetectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observations: list[Observation] = Field(min_length=1)


class DetectResponse(BaseModel):
    candidates: list[Candidate]
    forecasts: list[Forecast]
    hypotheses: list[Hypothesis]
    scored_observations: int

