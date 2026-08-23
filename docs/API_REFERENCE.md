# Python and API reference

## Minimal Python use

~~~python
from quasar_engine import DiscoveryPipeline, Observation

observations = [
    Observation(
        timestamp="2026-08-23T14:30:00Z",
        source_id="sensor_A",
        entity_id="entity_42",
        features={"signal_a": 1.4, "signal_b": 0.32},
        context={"domain": "example"},
    )
]

output = DiscoveryPipeline().process(observations)
~~~

The pipeline requires warm-up; one observation does not produce a forecast.

## Public objects

- Observation and Relation: common input contract.
- Candidate and Evidence: traceable statistical candidate.
- Hypothesis: structural statement, evidence, prediction, and rejection criterion.
- Forecast: probability, interval, horizon, and method.
- PipelineConfig: typed configuration.
- DiscoveryPipeline: local stateful orchestrator.
- PipelineOutput: scored observations, candidates, and hypotheses.

## YAML configuration

~~~python
from quasar_engine import DiscoveryPipeline, PipelineConfig

config = PipelineConfig.from_yaml("configs/base.yaml")
pipeline = DiscoveryPipeline(config)
~~~

Detector threshold, forecast horizon, logistic or ensemble forecast method, and calibration method are explicit configuration values.

## Research functions

The quasar_engine.research module exposes:

- run_multiseed;
- run_calibration_study;
- run_ablation_study;
- run_scalability_study.

quasar_engine.experiment exposes run_domain for registered synthetic data and run_observations for labeled Observation records.

## REST API

POST /detect receives an observations array and creates a new pipeline per request. GET /health returns status and version.

A pipeline per request avoids shared mutable state in the POC but is not a streaming architecture. The REST surface does not perform temporal calibration because labels are not available operationally.

