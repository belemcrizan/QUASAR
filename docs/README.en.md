# QUASAR - English overview

QUASAR (Quantified Uncertainty Analysis for Signals, Anomalies, and Regimes) is a local, domain-agnostic research POC for weak-signal discovery. It learns an expected background, measures distribution and dependency shifts, fuses evidence, produces probabilistic forecasts, and evaluates them on chronologically held-out data.

The same core runs on two synthetic domains: fraud/surveillance and astronomy. Labels are evaluation-only and cannot affect detection. Outputs preserve evidence, failed predictions, uncertainty, calibration metrics, baselines, seed, configuration hash, and runtime metadata.

Quick start:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
quasar demo --domain all --points 360 --seed 42
```

This POC does not establish causal discovery, real-world efficacy, scientific novelty, patentability, or production readiness.

