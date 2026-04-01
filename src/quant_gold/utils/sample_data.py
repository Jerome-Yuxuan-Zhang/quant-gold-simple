from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from quant_gold.data.contracts import DatasetSpec, StandardFrame


def generate_sample_standard_frames(dataset_specs: list[DatasetSpec]) -> list[StandardFrame]:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2019-01-01", periods=520)

    factor_rates = np.cumsum(rng.normal(0.0, 0.012, size=len(dates)))
    factor_risk = np.cumsum(rng.normal(0.0, 0.018, size=len(dates)))
    factor_inflation = np.cumsum(rng.normal(0.0, 0.01, size=len(dates)))

    gold = 1300 + 7.5 * factor_inflation - 6.0 * factor_rates + 2.0 * factor_risk
    gold = gold + np.linspace(0, 140, len(dates)) + rng.normal(0.0, 6.0, size=len(dates))

    lookup: dict[str, np.ndarray] = {
        "gold_close": gold,
        "silver_close": 15 + 0.012 * gold + rng.normal(0.0, 0.4, size=len(dates)),
        "yield_2y": 1.5 + 0.6 * factor_rates + rng.normal(0.0, 0.04, size=len(dates)),
        "yield_10y": 2.2 + 0.7 * factor_rates + rng.normal(0.0, 0.05, size=len(dates)),
        "real_yield_proxy": 0.8 + 0.5 * factor_rates - 0.2 * factor_inflation + rng.normal(0.0, 0.04, size=len(dates)),
        "breakeven_proxy": 2.0 + 0.25 * factor_inflation + rng.normal(0.0, 0.05, size=len(dates)),
        "usd_proxy": 100 + 0.8 * factor_rates - 0.25 * factor_risk + rng.normal(0.0, 0.3, size=len(dates)),
        "vix_proxy": 18 + 1.5 * np.abs(np.diff(np.r_[0, factor_risk])) * 20 + rng.normal(0.0, 0.7, size=len(dates)),
        "equity_proxy": 2600 + 24 * factor_risk - 10 * factor_rates + rng.normal(0.0, 18.0, size=len(dates)),
        "oil_close": 55 + 4.5 * factor_inflation + 1.2 * factor_risk + rng.normal(0.0, 1.3, size=len(dates)),
    }

    standard_frames: list[StandardFrame] = []
    for spec in dataset_specs:
        values = lookup.get(spec.name)
        if values is None:
            continue
        frame = pd.DataFrame({"date": dates, "value": values})
        frame["series_id"] = spec.name
        frame["source"] = spec.source
        frame["native_frequency"] = spec.native_frequency
        frame["unit"] = spec.unit
        frame["last_updated"] = dates.max().strftime("%Y-%m-%d")
        frame["description"] = spec.description
        standard_frames.append(StandardFrame(dataset_spec=replace(spec), frame=frame))
    return standard_frames

