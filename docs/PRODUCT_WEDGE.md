# Product wedge: market surveillance

## Status

This document records future product discovery. Market-surveillance code is not part of the current local POC.

## Why this wedge is stronger

Market surveillance has:

- a regulated and measurable operational pain;
- explicit evidence, audit, and human-review requirements;
- high cost from false positives and slow investigations;
- multiple weak signals across trades, entities, events, and market behavior;
- a buyer and workflow that can be identified;
- a natural need for calibrated prioritization rather than autonomous accusation.

Insider trading is a strong first use case, while the architecture should remain broader than one rule or instrument class.

## Candidate workflow

~~~mermaid
flowchart TD
    A["Trades + market + disclosures"] --> B["Domain adapter"]
    B --> C["QUASAR candidate score"]
    C --> D["Evidence package"]
    D --> E["Human investigation"]
    E --> F["Decision + outcome label"]
    F --> G["Temporal validation"]
~~~

## Product metrics

- confirmed-case recall;
- false-positive reduction;
- investigation time;
- lead time;
- evidence completeness;
- agreement with expert decisions;
- calibration by risk tier;
- auditability and reproducibility;
- infrastructure cost per million events.

## Boundary

QUASAR may prioritize and explain evidence. It must not accuse a person, close an alert, or take a regulated action without governed human review and validated domain controls.

Fraud remains a secondary wedge. Product implementation follows quantitative research gates, although interviews and workflow discovery can happen in parallel.

