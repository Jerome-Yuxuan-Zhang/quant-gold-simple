from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    source: str
    remote_id: str
    description: str
    native_frequency: str
    unit: str
    params: dict[str, Any] = field(default_factory=dict)

    def cache_key(self) -> str:
        param_part = "_".join(f"{key}-{value}" for key, value in sorted(self.params.items()))
        return f"{self.source}__{self.name}__{self.remote_id}__{param_part}".replace("/", "_")


@dataclass(frozen=True)
class RawPayload:
    dataset_spec: DatasetSpec
    raw_data: dict[str, Any]
    fetched_at: datetime


@dataclass(frozen=True)
class StandardFrame:
    dataset_spec: DatasetSpec
    frame: pd.DataFrame


@dataclass(frozen=True)
class FeatureSpec:
    rolling_windows: tuple[int, ...] = (5, 10, 20)
    zscore_window: int = 20
    exogenous_lag_days: int = 1


@dataclass(frozen=True)
class TargetSpec:
    forecast_horizon_days: int = 1


@dataclass(frozen=True)
class SplitSpec:
    train_fraction: float = 0.6
    validation_fraction: float = 0.2

    @property
    def test_fraction(self) -> float:
        return 1.0 - self.train_fraction - self.validation_fraction


def dataset_specs_from_config(payload: dict[str, Any]) -> list[DatasetSpec]:
    return [
        DatasetSpec(
            name=item["name"],
            source=item["source"],
            remote_id=item["remote_id"],
            description=item["description"],
            native_frequency=item["native_frequency"],
            unit=item["unit"],
            params=item.get("params", {}),
        )
        for item in payload["datasets"]
    ]


def utc_now() -> datetime:
    return datetime.now(UTC)

