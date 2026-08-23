# QUASAR Discovery Engine

**Quantified Uncertainty Analysis for Signals, Anomalies, and Regimes**

QUASAR is a local, domain-agnostic research POC for detecting weak, jointly emerging signals, producing probabilistic forecasts, and testing those forecasts on chronologically held-out data.

The name refers to quasars: distant astrophysical objects whose structure is inferred by separating background, noise, uncertainty, and accumulated evidence.

> Learn the expected background, measure how information structure changes, fuse independent evidence, forecast what should happen next, and let future data weaken or support the hypothesis.

## Project status

**Version:** 0.2.0 research POC  
**Runtime:** local Python; no API key, database, cloud account, or LLM required  
**Critical path:** deterministic numerical/statistical components only  
**Claims:** no causal discovery, real-world superiority, scientific novelty, patentability, or production readiness

QUASAR is intentionally positioned between a toy prototype and a research-ready system. It has a complete and testable workflow, but real datasets, stronger baselines, repeated seeds, and external validation are required before a paper-level claim.

## Plain-language explanation

Imagine a telescope pointed at a large universe of data. One unusual point may be noise. Several small changes that appear together and persist may deserve investigation.

QUASAR:

1. learns what normal behavior looks like from past observations;
2. measures changes in distributions, dependencies, entropy, and regimes;
3. combines those measurements into a traceable emergence score;
4. produces a probability for an event within a defined horizon;
5. calibrates that probability using a later chronological slice;
6. reveals a final held-out slice and records both successes and failures.

A candidate is not automatically fraud, failure, a market event, or an astronomical discovery. It is a statistical structure that deserves domain review.

## What v0.2.0 adds

| Research capability | Implementation |
|---|---|
| Multi-seed stability | Mean, sample standard deviation, and normal-approximation 95% confidence intervals |
| Calibration study | Temperature scaling, Platt scaling, and isotonic regression |
| Classical anomaly baseline | Dependency-free Isolation Forest baseline |
| Ablation study | Residual-only/no-fusion and leave-one-evidence-out variants |
| Scalability study | Configurable 10^3 to 10^6 observation runs, with a safety gate above 10^5 |
| Forecast variants | Configurable horizon and logistic/ensemble forecast mapping |
| Threshold experiments | CLI and YAML detector-threshold overrides |
| Real-data path | Local IEEE-CIS transaction CSV and NASA/MAST light-curve CSV conversion |
| Reporting | JSON, JSONL, and consolidated Markdown reports |
| International documentation | Public documentation and research roadmap in English |

## Quick start

### Windows PowerShell

~~~powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
quasar demo --domain all --points 360 --seed 42
~~~

If OneDrive or antivirus slows virtual-environment creation, place the environment outside the synchronized project folder:

~~~powershell
$venv = "$env:LOCALAPPDATA\quasar-venv"
py -3.13 -m venv $venv
& "$venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
quasar demo --domain all --points 360 --seed 42
~~~

### Linux or macOS

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
quasar demo --domain all --points 360 --seed 42
~~~

## Research commands

### Reproduce the two synthetic domains

~~~bash
quasar demo --domain all --points 360 --seed 42
~~~

### Run 30 seeds and document variance

~~~bash
quasar benchmark --domain all --points 360 --seeds 30 --seed-start 0
~~~

Generated files:

- multiseed.json: aggregate statistics;
- runs.jsonl: every seed and run ID;
- report.md: international, human-readable summary.

### Compare calibration methods

~~~bash
quasar calibrate --domain all --points 360 --seed 42 --methods temperature,platt,isotonic
~~~

The ECE target is below 0.05, but ECE must be interpreted together with Brier score, log loss, discrimination, coverage, and stability across seeds.

### Run evidence ablations

~~~bash
quasar ablate --domain all --points 360 --seed 42
~~~

Registered variants include full fusion, residual-only/no-fusion, and leave-one-evidence-out tests for entropy, mutual information, Jensen-Shannon divergence, change-point, and regime evidence.

### Test scalability

Start with a safe local study:

~~~bash
quasar scale --domain fraud --sizes 1000,10000,100000 --repeats 3
~~~

The one-million-observation experiment is explicit and opt-in:

~~~bash
quasar scale --domain fraud --sizes 1000,10000,100000,1000000 --repeats 3 --confirm-large
~~~

The large run can consume substantial memory and time. Run it on controlled hardware and record the environment.

### Test alternative forecasts and thresholds

~~~bash
quasar demo --domain all --forecast-method ensemble --horizon 8 --threshold 0.38 --calibration-method platt
~~~

## Real-data integration

QUASAR never downloads or redistributes third-party datasets automatically.

### IEEE-CIS Fraud Detection

Download train_transaction.csv from Kaggle under its applicable terms, then convert it:

~~~bash
quasar prepare-data --dataset ieee-cis --input data/ieee-cis/train_transaction.csv --output data/processed/ieee_cis.jsonl --max-rows 100000
quasar validate-data --input data/processed/ieee_cis.jsonl
quasar evaluate-data --input data/processed/ieee_cis.jsonl --domain fraud --data-name ieee_cis
~~~

Important: isFraud is a current-row classification label, not a true future-horizon label. This integration tests portability and discrimination; it must not be presented as an early-warning lead-time experiment.

### NASA/MAST light curves

Prepare a local CSV with time and flux; optional columns are flux_err, quality, label, and curve_id.

Use the NASA Exoplanet Archive for catalog/target metadata and MAST for Kepler or TESS light-curve files when appropriate; record both provenance sources.

~~~bash
quasar prepare-data --dataset nasa-lightcurve --input data/nasa/kepler_curve.csv --output data/processed/kepler_curve.jsonl --curve-id KIC-EXAMPLE
~~~

No transit label is inferred by the adapter. The user-supplied label and forecast horizon must be documented before evaluation. See [Real-data protocol](docs/REAL_DATA.md).

## Reference POC result

For 360 points and seed 42, the full pipeline produced:

| Domain | AUPRC | AUROC | Brier | ECE | Coverage |
|---|---:|---:|---:|---:|---:|
| Synthetic fraud | 0.664 | 0.935 | 0.055 | 0.069 | 0.929 |
| Synthetic astronomy | 0.759 | 0.957 | 0.047 | 0.082 | 0.881 |

v0.2.0 applies the same calibration protocol to score-based baselines. Under that fairer comparison, the residual-only baseline is stronger than full fusion on Brier and AUPRC for seed 42. This is an explicit negative result: the current weighted fusion is a transparent POC baseline, not the project's research contribution.

The next research question is whether a learned or theoretically grounded emergence function can outperform that baseline consistently across seeds and real domains.

## Architecture

~~~mermaid
flowchart TD
    A["Domain adapter"] --> B["Observation contract"]
    B --> C["Past-only background"]
    B --> D["Information dynamics"]
    C --> E["Evidence fusion"]
    D --> E
    E --> F["Candidate + structural hypothesis"]
    E --> G["Probabilistic forecast"]
    G --> H["Calibration + conformal interval"]
    H --> I["Held-out test + baselines"]
~~~

The identical core runs across domains. Adapters translate data but do not change the mathematical pipeline.

## Generated artifacts

Each evaluated domain writes results.json, run_manifest.json, predictions.jsonl, candidates.jsonl, hypotheses.jsonl, and report.md.

The manifest records the seed, package version, Python version, platform, and configuration hash. Failed predictions remain in predictions.jsonl.

## Tests

~~~bash
python -m unittest discover -s tests -v
RUN_QUASAR_BENCHMARKS=1 python -m unittest tests.benchmarks.test_performance -v
~~~

## Optional REST API

~~~bash
python -m pip install -e ".[api]"
quasar serve --host 127.0.0.1 --port 8000
~~~

Do not expose the POC API publicly without authentication, rate limits, isolation, audit controls, and a security review.

## Scientific governance

- Score the current observation before updating the background.
- Never use target_future in background, dynamics, emergence, or raw forecasting.
- Separate hypothesis, experiment, and conclusion.
- Preserve every seed, configuration, dataset version, parameter, and runtime.
- Report negative results and failed predictions.
- Do not call association causality.
- Do not claim novelty or superiority from synthetic experiments.
- Keep agents outside the quantitative critical path until the core passes its GO/NO-GO gates.

## Product and agentic boundaries

Market surveillance is the strongest future product wedge because it has a clear regulated pain, audit requirement, human-review workflow, and measurable operational cost. It remains outside the current POC.

Future agents may investigate candidates, search evidence, formulate testable hypotheses, and challenge explanations. They may not overwrite model probabilities or independently promote a candidate to a discovery.

## Documentation

- [Getting started](docs/GETTING_STARTED.md)
- [Non-technical guide](docs/FOR_NON_TECHNICAL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Scientific protocol](docs/SCIENTIFIC_PROTOCOL.md)
- [Experiments](docs/EXPERIMENTS.md)
- [Real-data protocol](docs/REAL_DATA.md)
- [Research roadmap](docs/RESEARCH_ROADMAP.md)
- [Adding a domain](docs/ADDING_A_DOMAIN.md)
- [Python/API reference](docs/API_REFERENCE.md)
- [Product wedge](docs/PRODUCT_WEDGE.md)
- [Future agentic layer](docs/AGENTIC_LAYER.md)
- [Limitations](docs/LIMITATIONS.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Security policy](SECURITY.md)
- [Citation metadata](CITATION.cff)

## License

Apache-2.0. The license is not a finding of originality, freedom to operate, or patentability. Complete literature review, prior-art search, and legal review before making intellectual-property claims.
