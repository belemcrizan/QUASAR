"""End-to-end local discovery pipeline."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict, deque
from dataclasses import dataclass

from quasar_engine.core.background import BACKGROUNDS, BackgroundModel
from quasar_engine.core.contract.candidate import Candidate
from quasar_engine.core.contract.forecast import Forecast
from quasar_engine.core.contract.hypothesis import Hypothesis
from quasar_engine.core.contract.observation import Observation
from quasar_engine.core.dynamics import DynamicalEvidence, InformationDynamicsEngine
from quasar_engine.core.emergence import EmergenceDetector, EmergenceScore
from quasar_engine.core.forecast.probabilistic import LogisticEmergenceForecaster
from quasar_engine.core.pipeline.config import PipelineConfig
from quasar_engine.core.pipeline.hooks import NullHook, PipelineHook


@dataclass(frozen=True, slots=True)
class ScoredObservation:
    observation: Observation
    emergence: EmergenceScore
    forecast: Forecast
    candidate: Candidate | None
    hypothesis: Hypothesis | None


@dataclass(frozen=True, slots=True)
class PipelineOutput:
    scored: tuple[ScoredObservation, ...]
    candidates: tuple[Candidate, ...]
    hypotheses: tuple[Hypothesis, ...]


class DiscoveryPipeline:
    """Coordinates background, dynamics, evidence fusion, and forecasting.

    Important: ground-truth labels are never read in this class. They are only
    revealed later by the validation layer.
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        background: BackgroundModel | None = None,
        hook: PipelineHook | None = None,
    ) -> None:
        self.config = config or PipelineConfig()
        bg = self.config.background
        self.background = background or BACKGROUNDS.create(
            bg.model, window=bg.window, min_history=bg.min_history, robust=bg.robust
        )
        self.dynamics = InformationDynamicsEngine(
            recent_window=self.config.dynamics.recent_window,
            bins=self.config.dynamics.bins,
        )
        self.detector = EmergenceDetector(
            self.config.detector.weights, self.config.detector.threshold
        )
        self.forecaster = LogisticEmergenceForecaster(
            threshold=self.config.detector.threshold,
            slope=self.config.forecast.slope,
        )
        history_size = max(bg.window, 2 * self.config.dynamics.recent_window + 2)
        self._history: dict[str, deque[Observation]] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        self.hook = hook or NullHook()

    def reset(self) -> None:
        self.background.reset()
        self._history.clear()

    def process(self, observations: list[Observation]) -> PipelineOutput:
        ordered = sorted(observations, key=lambda item: item.timestamp)
        scored: list[ScoredObservation] = []
        candidates: list[Candidate] = []
        hypotheses: list[Hypothesis] = []

        for observation in ordered:
            snapshot = self.background.score(observation)
            history = list(self._history[observation.source_id])
            dynamics = (
                self.dynamics.evaluate(history, observation)
                if snapshot.ready
                else DynamicalEvidence()
            )

            if snapshot.ready:
                emergence = self.detector.evaluate(snapshot, dynamics)
                probability = self.forecaster.predict_probability(emergence.score)
                uncertainty = min(0.40, 0.10 + 1.0 / math.sqrt(snapshot.sample_count + 1))
                candidate = self._candidate(observation, emergence) if emergence.is_candidate else None
                hypothesis = self._hypothesis(candidate) if candidate else None
                forecast = Forecast(
                    observation_id=observation.observation_id,
                    candidate_id=candidate.candidate_id if candidate else None,
                    probability=probability,
                    lower=max(0.0, probability - uncertainty),
                    upper=min(1.0, probability + uncertainty),
                    horizon_steps=self.config.forecast.horizon_steps,
                    method="logistic-emergence-v0",
                    calibrated=False,
                )
                record = ScoredObservation(observation, emergence, forecast, candidate, hypothesis)
                scored.append(record)
                if candidate and hypothesis:
                    candidates.append(candidate)
                    hypotheses.append(hypothesis)
                    self.hook.on_candidate(candidate)

            # Update happens strictly after scoring to avoid using the current point as background.
            self.background.update(observation)
            self._history[observation.source_id].append(observation)

        return PipelineOutput(tuple(scored), tuple(candidates), tuple(hypotheses))

    @staticmethod
    def _candidate(observation: Observation, emergence: EmergenceScore) -> Candidate:
        digest = hashlib.sha256(
            f"{observation.observation_id}|{emergence.score:.10f}".encode("utf-8")
        ).hexdigest()[:20]
        return Candidate(
            candidate_id=f"cand_{digest}",
            observation_id=observation.observation_id,
            timestamp=observation.timestamp,
            source_id=observation.source_id,
            entity_id=observation.entity_id,
            domain=str(observation.context.get("domain", "unknown")),
            score=emergence.score,
            evidence=emergence.evidence,
        )

    def _hypothesis(self, candidate: Candidate) -> Hypothesis:
        strongest = sorted(candidate.evidence, key=lambda item: item.normalized_value, reverse=True)[:3]
        evidence_lines = tuple(
            f"{item.metric}={item.normalized_value:.3f}" for item in strongest
        )
        return Hypothesis(
            candidate_id=candidate.candidate_id,
            statement=(
                f"A joint statistical structure may be emerging in source {candidate.source_id}; "
                "this is an association candidate, not a causal conclusion."
            ),
            evidence_for=evidence_lines,
            evidence_against=("No domain explanation has been independently verified yet.",),
            testable_prediction=(
                f"A labeled event should occur within {self.config.forecast.horizon_steps} steps."
            ),
            rejection_criterion=(
                "Reject or weaken if the held-out future contains no event and repeated temporal "
                "validation does not beat the registered baselines."
            ),
            causal_claim=False,
        )
