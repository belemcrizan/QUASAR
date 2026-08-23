# Limitations and risks

## Scientific limitations

- Synthetic generators may align with detector assumptions.
- Histogram estimates in small windows have high variance.
- Temperature scaling optimizes log loss, not ECE directly.
- Isotonic calibration can overfit small calibration slices and create ties.
- Platt scaling assumes a parametric monotonic relationship.
- Conformal coverage is finite-sample and marginal, not conditional by subgroup.
- Lead time depends on event-onset and horizon definitions.
- Normal-approximation confidence intervals are limited for small seed counts.
- The compact Isolation Forest must be compared with maintained implementations.
- The weighted fusion has not established improvement over residual-only detection.

## Engineering limitations

- State is in memory and resets with the process.
- Processing returns all scored observations, limiting million-row memory efficiency.
- Missing numeric features are supported by the core, but real-data preprocessing remains domain specific.
- There is no concurrency control, authentication, rate limiting, queue, or idempotency.
- The optional API is batch-oriented.
- Scalability results are local and hardware dependent.
- No automatic dataset download, FITS processing, or categorical encoding is provided.

## Use limitations

- Do not use the POC to block transactions, diagnose health, trade securities, or announce scientific discoveries without independent validation and appropriate controls.
- A high score is not a causal explanation.
- IEEE-CIS current-row labels do not support early-warning lead-time claims.
- Do not connect a decision-making LLM before preserving evidence, rejection criteria, audit, and human review.

## Publication limitations

The project is not currently ICLR-ready. A top-tier paper needs a clear mathematical or methodological contribution, real public benchmarks, stronger baselines, repeated seeds, ablations, scalability, and honest comparison.

## Licensing and novelty

Apache-2.0 governs code use but does not establish originality, freedom to operate, or patentability. Complete literature review, prior-art search, dataset-license review, and legal review before public intellectual-property claims.

