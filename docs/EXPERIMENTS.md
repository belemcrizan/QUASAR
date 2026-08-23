# Experiments

## A: synthetic fraud and surveillance

Features include log transaction amount, velocity, counterparty risk, and network density. Three episodes are injected with distributed precursors. The experiment tests weak-signal combination; it is not a faithful simulation of a financial institution.

~~~bash
quasar demo --domain fraud --points 360 --seed 42
~~~

## B: synthetic astronomy

Features include flux, color index, spectral width, and local background. Three synthetic transients have moderate precursors. The experiment tests core transfer; it does not discover a real astronomical object.

~~~bash
quasar demo --domain astronomy --points 360 --seed 42
~~~

## Multi-seed study

~~~bash
quasar benchmark --domain all --points 360 --seeds 30 --seed-start 0
~~~

The output includes an aggregate JSON report, one JSONL row per run, and a Markdown report. Confidence intervals are clamped to valid ranges for bounded metrics.

## Calibration study

~~~bash
quasar calibrate --domain all --methods temperature,platt,isotonic
~~~

Methods use identical observations and time splits. The held-out test is for comparison reporting only; do not select the best method on that test and reuse the same numbers as an unbiased final result.

## Ablation study

~~~bash
quasar ablate --domain all --points 360 --seed 42
~~~

The protocol fixes the seed, observations, split, and all non-ablated settings. Use repeated-seed ablations before strong conclusions.

## Scalability study

~~~bash
quasar scale --domain fraud --sizes 1000,10000,100000 --repeats 3
~~~

For one million rows, add --confirm-large. Record hardware, Python version, platform, package version, configuration hash, warm-up, and whether data generation is included in the profile.

## Artifact interpretation

predictions.jsonl is the main audit trail. It stores the partition, raw and calibrated probabilities, intervals, evidence metrics, and revealed evaluation label. candidates.jsonl contains only above-threshold points and must never replace evaluation of every prediction.

## Reproducibility rule

Do not change seeds, thresholds, weights, horizons, or methods after inspecting the final test unless the next experiment receives a new untouched test. Record exploration separately from confirmation.

