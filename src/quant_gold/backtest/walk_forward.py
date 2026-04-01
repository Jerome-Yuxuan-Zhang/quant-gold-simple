from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from quant_gold.models.model_selection import build_classifier


@dataclass(frozen=True)
class WalkForwardConfig:
    model_name: str
    model_params: dict[str, Any]
    feature_columns: list[str]
    target_horizon_days: int
    lookback_years: int
    initial_train_years: int
    retrain_frequency_days: int


def generate_walk_forward_predictions(model_frame: pd.DataFrame, config: WalkForwardConfig) -> pd.DataFrame:
    frame = model_frame.sort_values("date").reset_index(drop=True).copy()
    end_date = frame["date"].max()
    start_date = end_date - pd.DateOffset(years=config.lookback_years)
    frame = frame.loc[frame["date"] >= start_date].reset_index(drop=True)

    first_trade_date = frame["date"].min() + pd.DateOffset(years=config.initial_train_years)
    rebalance_mask = frame["date"] >= first_trade_date
    rebalance_indices = frame.index[rebalance_mask].tolist()[:: config.retrain_frequency_days]
    if not rebalance_indices:
        fallback_start = max(int(len(frame) * 0.5), 60)
        rebalance_indices = list(range(fallback_start, len(frame), config.retrain_frequency_days))

    predictions: list[pd.DataFrame] = []
    for start_idx, rebalance_idx in enumerate(rebalance_indices):
        train_frame = frame.loc[frame["date"] < frame.loc[rebalance_idx, "date"]].copy()
        if train_frame.empty:
            continue
        next_rebalance_idx = (
            rebalance_indices[start_idx + 1]
            if start_idx + 1 < len(rebalance_indices)
            else len(frame)
        )
        predict_frame = frame.iloc[rebalance_idx:next_rebalance_idx].copy()
        if predict_frame.empty:
            continue

        model = build_classifier(config.model_name, config.model_params)
        model.fit(train_frame[config.feature_columns], train_frame["target_direction_1d"])
        predict_frame["predicted_direction"] = model.predict(predict_frame[config.feature_columns]).astype(int)
        predictions.append(predict_frame)

    if not predictions:
        raise ValueError("No walk-forward predictions were generated.")

    prediction_frame = pd.concat(predictions, ignore_index=True)
    prediction_frame["signal"] = prediction_frame["predicted_direction"]
    prediction_frame["position"] = _build_horizon_aligned_position(
        prediction_frame["signal"],
        config.target_horizon_days,
    )
    prediction_frame["model_name"] = config.model_name
    prediction_frame["target_horizon_days"] = config.target_horizon_days
    return prediction_frame


def _build_horizon_aligned_position(signal: pd.Series, horizon_days: int) -> pd.Series:
    if horizon_days <= 1:
        return signal.shift(1).fillna(0.0).astype(float)

    active_signals = [signal.shift(step).fillna(0.0) for step in range(1, horizon_days + 1)]
    position = sum(active_signals) / float(horizon_days)
    return position.clip(lower=0.0, upper=1.0).astype(float)
