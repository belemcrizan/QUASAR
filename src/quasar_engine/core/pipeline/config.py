"""Typed configuration with YAML loading."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class BackgroundConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = "statistical"
    window: int = Field(default=48, ge=8)
    min_history: int = Field(default=24, ge=3)
    robust: bool = True


class DynamicsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recent_window: int = Field(default=12, ge=4)
    bins: int = Field(default=8, ge=2, le=64)


class DetectorConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    threshold: float = Field(default=0.34, gt=0.0, lt=1.0)
    weights: dict[str, float] = Field(
        default_factory=lambda: {
            "residual": 0.30,
            "entropy_change": 0.10,
            "mutual_info_change": 0.12,
            "js_divergence": 0.20,
            "change_point": 0.18,
            "regime_change": 0.10,
        }
    )


class ForecastConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    horizon_steps: int = Field(default=4, ge=1)
    method: Literal["logistic", "ensemble"] = "logistic"
    slope: float = Field(default=9.0, gt=0.0)
    ensemble_slopes: tuple[float, ...] = (5.0, 9.0, 15.0)
    conformal_coverage: float = Field(default=0.90, gt=0.5, lt=1.0)


class ValidationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    calibration_method: Literal["temperature", "platt", "isotonic"] = "temperature"
    calibration_fraction: float = Field(default=0.20, gt=0.0, lt=0.5)
    test_fraction: float = Field(default=0.25, gt=0.0, lt=0.5)
    calibration_bins: int = Field(default=10, ge=2, le=50)


class PipelineConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    dynamics: DynamicsConfig = Field(default_factory=DynamicsConfig)
    detector: DetectorConfig = Field(default_factory=DetectorConfig)
    forecast: ForecastConfig = Field(default_factory=ForecastConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "PipelineConfig":
        source = Path(path)
        with source.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return cls.model_validate(data)
