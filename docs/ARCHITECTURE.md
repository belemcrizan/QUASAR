# Architecture

## Design principles

1. **Domain-independent core.** Adapters translate records; they do not rewrite the mathematics.
2. **Past-only scoring.** The current observation is scored before it updates the background.
3. **Evidence before narrative.** Candidates preserve numerical contributions.
4. **Probability before certainty.** Forecasts are calibrated and accompanied by intervals.
5. **Automated falsification.** Chronologically held-out observations test forecasts.
6. **Research separation.** Multi-seed, calibration, ablation, and scale studies wrap the core.
7. **Integration at the edges.** CLI, API, reports, and storage depend on the core; the core does not depend on them.

## Runtime flow

~~~mermaid
flowchart TD
    A["Raw domain record"] --> B["Domain adapter"]
    B --> C["Observation contract"]
    C --> D["Past-only background"]
    C --> E["Information dynamics"]
    D --> F["Robust residuals"]
    E --> G["H, I, JS, change, regime"]
    F --> H["Evidence fusion"]
    G --> H
    H --> I["Candidate + structural hypothesis"]
    H --> J["Raw probability"]
    J --> K["Chronological calibration"]
    K --> L["Held-out evaluation"]
~~~

## Research wrapper

~~~mermaid
flowchart TD
    A["Fixed protocol"] --> B["Multi-seed study"]
    A --> C["Calibration study"]
    A --> D["Ablation study"]
    A --> E["Scalability study"]
    B --> F["JSON + Markdown reports"]
    C --> F
    D --> F
    E --> F
~~~

## State and streaming

DiscoveryPipeline keeps a bounded history for each source_id. Background score is called before background update, preventing the current point from silently entering its own baseline.

A future production implementation may persist state in a stream processor, database, or managed state store. No provider is part of the core contract.

## Complexity

For F features, window W, and N observations, the current implementation is approximately O(N × (F×W + F²×W)). Mutual-information pairs are capped at the first four features. Per-source history is bounded.

The current pipeline returns all scored observations, so the one-million-row study may be memory constrained. The scale command intentionally requires explicit confirmation above 100,000 rows; streaming output is a future engineering improvement.

## Dependency boundary

The mandatory runtime uses NumPy, Pydantic, and PyYAML. FastAPI and Uvicorn are optional. Platt scaling, isotonic regression, and the compact Isolation Forest baseline are implemented without adding scikit-learn to the required runtime.

## Future extensions

- PELT and Bayesian change-point detection;
- maintained-library benchmark parity for Isolation Forest;
- conventional forecasting and domain-specific baselines;
- streaming state and incremental artifact writing;
- cloud storage and SQL metadata adapters;
- authentication, idempotency, tracing, SLOs, and security review;
- governed investigation agents only after quantitative gates pass.

