"""Chronological train/calibration/test slicing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemporalSplit:
    calibration_start: int
    test_start: int
    total: int

    @classmethod
    def create(
        cls, total: int, calibration_fraction: float = 0.20, test_fraction: float = 0.25
    ) -> "TemporalSplit":
        if total < 20:
            raise ValueError("at least 20 scored observations are required")
        if not 0 < calibration_fraction < 0.5 or not 0 < test_fraction < 0.5:
            raise ValueError("calibration/test fractions must be in (0, 0.5)")
        test_size = max(5, int(total * test_fraction))
        calibration_size = max(5, int(total * calibration_fraction))
        test_start = total - test_size
        calibration_start = test_start - calibration_size
        if calibration_start <= 0:
            raise ValueError("not enough pre-calibration observations")
        return cls(calibration_start, test_start, total)

    @property
    def calibration(self) -> slice:
        return slice(self.calibration_start, self.test_start)

    @property
    def test(self) -> slice:
        return slice(self.test_start, self.total)

