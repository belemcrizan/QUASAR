# Real-data protocol

## Boundary

QUASAR provides local ingestion paths but does not download, bundle, or redistribute third-party datasets. Users are responsible for access terms, licenses, checksums, storage, and citations.

## IEEE-CIS Fraud Detection

Expected source: Kaggle train_transaction.csv.

~~~bash
quasar prepare-data --dataset ieee-cis --input data/ieee-cis/train_transaction.csv --output data/processed/ieee_cis.jsonl --max-rows 100000
~~~

The adapter maps TransactionDT to an arbitrary UTC epoch plus relative seconds, TransactionID to entity_id, selected numeric transaction fields to features, and isFraud to target_future when present.

### Critical semantic limitation

isFraud labels the current transaction. It is not a future-horizon target. Therefore:

- AUROC/AUPRC can support a portability or classification-style benchmark;
- lead time must not be interpreted as early warning;
- a true surveillance forecast requires constructing labels from later events and freezing that construction before testing.

For a full IEEE-CIS experiment, add the identity table, missingness indicators, cardinality-safe categorical encoding, chronological group controls, and a dataset checksum.

## NASA/MAST light curves

The NASA Exoplanet Archive is useful for confirmed-planet and target metadata, while Kepler/TESS light-curve files are commonly obtained through MAST. Record both sources when the experiment joins catalog labels with observational curves.

The adapter accepts a preprocessed local CSV:

| Column | Required | Meaning |
|---|---|---|
| time | yes | Relative days |
| flux | yes | Flux measurement |
| flux_err | no | Measurement uncertainty |
| quality | no | Quality flag or numeric score |
| label | no | User-supplied evaluation label |
| curve_id | no | Source/light-curve identity |

~~~bash
quasar prepare-data --dataset nasa-lightcurve --input data/nasa/kepler_curve.csv --output data/processed/kepler_curve.jsonl --curve-id KIC-EXAMPLE
~~~

The adapter does not download FITS files, detrend curves, infer transit labels, or choose a forecast horizon. Those choices must be documented in the experiment protocol.

## Validation sequence

1. Record source URL, access date, license, version, and SHA-256.
2. Preserve the raw file as read-only.
3. Create a deterministic conversion configuration.
4. Validate the produced Observation JSONL.
5. Define target semantics and forecast horizon before evaluation.
6. Split chronologically and prevent entity leakage.
7. Run registered baselines and QUASAR under the same split.
8. Report negative results and missing-data exclusions.

## Commands

~~~bash
quasar validate-data --input data/processed/example.jsonl
quasar evaluate-data --input data/processed/example.jsonl --domain fraud --data-name registered_dataset_v1
~~~

evaluate-data requires target_future on every observation. Use quasar run for unlabeled operational scoring.
