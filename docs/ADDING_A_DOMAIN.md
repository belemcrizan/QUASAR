# Adding a domain

## 1. Define the question

Write the future event, legitimate horizon, unit of observation, source boundary, and human decision the system will support. Do not begin with features.

## 2. Start from the template

Use src/quasar_engine/adapters/template/adapter.py. The adapter must convert each domain record into Observation without importing detector internals.

## 3. Map the contract

- timestamp: when the observation became available;
- source_id: stream, sensor, or system sharing one background;
- entity_id: optional observed entity;
- features: finite numeric values in the current POC;
- relations: optional known relationships;
- context: metadata that cannot act as a hidden label;
- target_future: optional evaluation-only label.

## 4. Preserve target semantics

Document whether target_future means a current class, an event inside a future window, a regime transition, or another outcome. Do not report lead time from a current-row classification label.

## 5. Validate data

~~~bash
quasar validate-data --input observations.jsonl
~~~

## 6. Score without labels

~~~bash
quasar run --input observations.jsonl --output-dir runs/my-domain
~~~

## 7. Register evaluation

Add dataset version, license, checksum, seed set, horizon, baselines, metrics, and stopping criteria under experiments.

~~~bash
quasar evaluate-data --input labeled_observations.jsonl --domain my-domain --data-name dataset_v1
~~~

## 8. Test core independence

Domain-specific feature engineering belongs in the adapter. Do not copy core modules. If the mathematics must change, register that change as a new hypothesis and rerun previous-domain ablations.

## 9. Measure transfer

Report unchanged core code, adapter lines and complexity, feature requirements, calibration shift, metric degradation, and compute change. Architecture reuse alone is not scientific generalization.

