"""Local CSV ingestion for preprocessed NASA/MAST Kepler or TESS light curves."""

from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quasar_engine.core.contract.observation import Observation


def _number(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def load_nasa_lightcurve_csv(
    path: str | Path,
    max_rows: int | None = None,
    curve_id: str | None = None,
) -> list[Observation]:
    """Convert a preprocessed light-curve CSV into Observation records.

    Required columns are `time` and `flux`. Optional columns are `flux_err`,
    `quality`, `label`, and `curve_id`. Time is interpreted as relative days.
    The adapter does not download FITS files or infer transit labels.
    """
    source = Path(path)
    observations: list[Observation] = []
    arbitrary_epoch = datetime(2009, 3, 7, tzinfo=timezone.utc)
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        lookup = {name.lower(): name for name in (reader.fieldnames or ())}
        missing = {"time", "flux"} - set(lookup)
        if missing:
            raise ValueError(f"light-curve CSV is missing columns: {', '.join(sorted(missing))}")
        for row_index, row in enumerate(reader):
            if max_rows is not None and row_index >= max_rows:
                break
            relative_days = _number(row.get(lookup["time"]))
            flux = _number(row.get(lookup["flux"]))
            if relative_days is None or flux is None:
                continue
            features = {"flux": flux}
            for optional in ("flux_err", "quality"):
                column = lookup.get(optional)
                number = _number(row.get(column)) if column else None
                if number is not None:
                    features[optional] = number
            label_column = lookup.get("label")
            label_value = _number(row.get(label_column)) if label_column else None
            label = int(label_value) if label_value is not None else None
            source_curve = curve_id or row.get(lookup.get("curve_id", "")) or source.stem
            observations.append(
                Observation(
                    timestamp=arbitrary_epoch + timedelta(days=relative_days),
                    source_id=f"nasa_lightcurve:{source_curve}",
                    entity_id=str(source_curve),
                    features=features,
                    context={
                        "domain": "astronomy",
                        "dataset": "NASA/MAST preprocessed light curve",
                        "synthetic": False,
                        "event_now": int(label or 0),
                        "target_semantics": "user-supplied label; verify horizon before lead-time use",
                    },
                    target_future=label,
                )
            )
    if not observations:
        raise ValueError("no valid light-curve observations were produced")
    return observations

