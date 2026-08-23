# Contributing

## Before code

Open an issue describing the hypothesis, domain, dataset, temporal split, metrics, baselines, and leakage risk. A change that improves only one observed seed should not be merged as a research improvement.

## Local checks

~~~bash
python -m pip install -e ".[dev]"
python -m compileall -q src tests scripts experiments
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
~~~

## Rules

- preserve the public API in quasar_engine.__init__;
- keep adapters outside the core;
- never use target_future in background, dynamics, emergence, or raw forecast;
- add a test for every defect fix;
- record seeds, dataset versions, configurations, and hardware;
- preserve failed predictions and negative results;
- use causal language only with an appropriate causal design;
- justify mandatory dependencies;
- keep research-study orchestration separate from DiscoveryPipeline;
- do not add agents to the quantitative critical path.

## Research pull requests

A research PR should include:

1. hypothesis and rejection criterion;
2. baseline and ablation plan;
3. unchanged test protocol;
4. repeated-seed results;
5. compute and memory impact;
6. limitations and negative results;
7. report artifacts or deterministic commands.

## Commit examples

Use messages such as feat: add PELT baseline, fix: prevent temporal leakage, research: add 30-seed report, or docs: clarify IEEE-CIS target semantics.

