# Scientific protocol

## POC question

Can one unchanged core transform moderate, distributed signals into useful temporal forecasts in two synthetic domains, while preserving uncertainty and excluding future labels from detection?

## Registered hypotheses

- **H1:** evidence fusion improves at least one decision-relevant metric over registered baselines.
- **H2:** the same core transfers across the two domains without code changes.
- **H3:** calibrated forecasts produce positive lead time for at least some events.
- **H4:** improvements remain stable across at least 30 seeds.
- **H5:** a future learned or theoretically grounded emergence function improves over residual-only detection on real and synthetic domains.

H1 through H3 are POC hypotheses. H4 and H5 are research-roadmap hypotheses. None imply causality.

## Chronological protocol

~~~mermaid
timeline
    title Leakage-resistant evaluation
    Background : learn expected behavior from past observations
    Prediction : score before updating state
    Calibration : fit probability mapping on a later slice
    Test : evaluate the final held-out slice
    Report : preserve positive and negative outcomes
~~~

Default scored-sequence partitions:

- pre-calibration history;
- 20% chronological calibration slice;
- 25% final held-out test slice.

## Metrics

| Family | Metrics | Interpretation |
|---|---|---|
| Probability quality | Brier, log loss | Lower is better |
| Calibration | ECE, empirical coverage | ECE lower; coverage compared with target |
| Discrimination | AUROC, AUPRC | AUPRC is important for rare events |
| Operational | Precision, recall, FPR, lead time | Threshold and domain dependent |
| Stability | Mean, standard deviation, 95% CI | Repeated seeds |
| Compute | p50/p95 runtime, memory, throughput | Local feasibility, not cloud cost |

An ECE below 0.05 is an aspirational target, not a standalone acceptance criterion. Calibration can improve ECE while harming ranking, sharpness, or usefulness.

## Registered baselines

- constant calibration-slice event rate;
- robust residual-only score;
- standardized mean-change score;
- dependency-free Isolation Forest;
- future: maintained-library Isolation Forest parity;
- future: PELT, conventional forecasting, representation models, and domain-specific methods.

All score-based v0.2 baselines use the same chronological calibration method as the full pipeline for a fairer probability comparison.

## Ablations

The registered ablation study includes:

- full fusion;
- residual-only/no-fusion;
- without entropy change;
- without mutual-information change;
- without Jensen-Shannon divergence;
- without change-point evidence;
- without regime-change evidence.

The current residual-only baseline can outperform full weighted fusion. This negative result is preserved and motivates a better emergence formulation.

## Multi-seed analysis

Run at least 30 seeds. Report every run ID, mean, sample standard deviation, and 95% normal-approximation confidence interval. Do not remove unfavorable seeds.

For publication, consider bootstrap or Student-t intervals, multiple-comparison controls, and pre-registered selection rules.

## GO/NO-GO

Advance the research method when gains are stable across seeds, survive real-data baselines, remain calibratable, provide useful lead time or another measurable advantage, transfer across domains, and fit the compute budget.

Reformulate or stop when gains disappear against simple methods, adapters leak domain logic into the core, calibration remains unstable, cost grows faster than value, or agents produce narratives unsupported by quantitative evidence.

