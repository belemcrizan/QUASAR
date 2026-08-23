# Research roadmap

## Phase 0: freeze the POC

Tag v0.2.0 after tests, packaging checks, and English documentation pass. Treat configuration and CLI outputs as versioned research interfaces.

## Phase 1: statistical hardening

- Run at least 30 seeds per synthetic domain.
- Add repeated-seed ablations.
- Compare temperature, Platt, and isotonic calibration without reusing the final test for method selection.
- Add maintained-library parity tests for Isolation Forest.
- Target ECE below 0.05 while preserving Brier, log loss, ranking, coverage, and operational usefulness.

**Gate:** stable metrics and transparent negative results.

## Phase 2: real-data validation

- IEEE-CIS Fraud Detection for portability and classification-style evaluation.
- NASA/MAST Kepler or TESS light curves with explicit preprocessing and label semantics.
- Dataset versions, licenses, checksums, and chronological splits.
- Domain-specific baselines.

**Gate:** measurable benefit or justified complementarity beyond simple methods.

## Phase 3: the research contribution

The current weighted fusion is not sufficient novelty for a top-tier ML paper. Candidate contributions include:

1. a learned emergence function with calibration constraints;
2. a new information-organization metric over changing dependencies and regimes;
3. domain-general evidence fusion with uncertainty guarantees;
4. cross-domain transfer with minimal adaptation;
5. falsifiable multi-horizon emergence forecasting.

Select one contribution, formalize it mathematically, and pre-register its falsification criteria.

## Phase 4: scalability and robustness

- 10^3, 10^4, 10^5, and 10^6 observations;
- high source cardinality;
- missing data and distribution shift;
- p50/p95/p99 latency, memory, CPU, and throughput;
- incremental processing and streaming artifact output;
- adversarial and contamination stress tests where relevant.

**Gate:** cost compatible with the value of the candidate signals.

## Phase 5: generalization

Add process mining/RPA and supply-chain/log domains only after the first two real domains are stable. Measure unchanged core code, adapter complexity, and performance loss.

**Gate:** meaningful transfer without rewriting the core.

## Phase 6: research release

- technical paper;
- reproducibility package;
- public library/API documentation;
- model and dataset cards where applicable;
- limitations and negative-result appendix.

## Phase 7: product wedge

Market surveillance is the primary candidate, with fraud as a secondary vertical. Product discovery may run in parallel, but product implementation follows quantitative validation.

## Phase 8: agentic investigation

Add investigation, evidence, hypothesis, critic, and explanation agents. Agents remain outside model scoring and cannot promote a discovery without quantitative validation and human review.

