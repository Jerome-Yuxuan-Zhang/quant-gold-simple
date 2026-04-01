from __future__ import annotations

import pandas as pd

from quant_gold.data.contracts import TargetSpec


class TargetBuilder:
    def build(
        self,
        feature_frame: pd.DataFrame,
        target_spec: TargetSpec,
        required_feature_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        horizon = target_spec.forecast_horizon_days
        model_frame = feature_frame.copy()
        future_returns = [model_frame["return_1d"].shift(-step) for step in range(1, horizon + 1)]
        model_frame["target_return_1d"] = sum(future_returns)
        model_frame["target_direction_1d"] = (model_frame["target_return_1d"] > 0).astype(int)
        model_frame["target_horizon_days"] = horizon
        if required_feature_columns is None:
            subset = list(model_frame.columns)
        else:
            subset = [column for column in required_feature_columns if column in model_frame.columns]
            subset.extend(["target_return_1d", "target_direction_1d"])
        model_frame = model_frame.dropna(subset=subset).reset_index(drop=True)
        return model_frame
