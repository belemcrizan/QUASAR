"""Local ingestion path for the IEEE-CIS Fraud Detection transaction CSV.

The Kaggle dataset must be downloaded by the user under its own terms. QUASAR
does not download, redistribute, or bundle the dataset.
"""

from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quasar_engine.core.contract.observation import Observation


DEFAULT_NUMERIC_FEATURES = (
    "TransactionAmt",
    "dist1",
    "dist2",
    "C1",
    "C2",
    "D1",
    "D2",
    "V1",
)


def _finite_number(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def load_ieee_cis_transactions(
    path: str | Path,
    max_rows: int | None = None,
    feature_names: tuple[str, ...] = DEFAULT_NUMERIC_FEATURES,
) -> list[Observation]:
    """Convert `train_transaction.csv` rows into the common contract.

    `isFraud` is mapped to `target_future` for a classification-style integration
    benchmark. It is not a genuine future-horizon label, so lead-time results from
    this conversion must not be interpreted as early-warning performance.
    """
    source = Path(path)
    observations: list[Observation] = []
    arbitrary_epoch = datetime(2017, 12, 1, tzinfo=timezone.utc)
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"TransactionDT", "TransactionID"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"IEEE-CIS CSV is missing columns: {', '.join(sorted(missing))}")
        for row_index, row in enumerate(reader):
            if max_rows is not None and row_index >= max_rows:
                break
            transaction_seconds = _finite_number(row.get("TransactionDT"))
            if transaction_seconds is None:
                continue
            features: dict[str, float] = {}
            for name in feature_names:
                number = _finite_number(row.get(name))
                if number is not None:
                    features[name] = math.log1p(max(number, 0.0)) if name == "TransactionAmt" else number
            if not features:
                continue
            label_value = _finite_number(row.get("isFraud"))
            label = int(label_value) if label_value is not None else None
            observations.append(
                Observation(
                    timestamp=arbitrary_epoch + timedelta(seconds=transaction_seconds),
                    source_id="ieee_cis_transactions",
                    entity_id=str(row.get("TransactionID") or f"row_{row_index}"),
                    features=features,
                    context={
                        "domain": "fraud",
                        "dataset": "IEEE-CIS Fraud Detection",
                        "synthetic": False,
                        "event_now": int(label or 0),
                        "target_semantics": "current-row classification, not future lead time",
                    },
                    target_future=label,
                )
            )
    if not observations:
        raise ValueError("no valid IEEE-CIS observations were produced")
    return observations

