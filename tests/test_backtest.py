from pathlib import Path

import pandas as pd

from quant_gold.backtest.simulator import run_long_flat_backtest
from quant_gold.backtest.walk_forward import (
    WalkForwardConfig,
    _build_horizon_aligned_position,
    generate_walk_forward_predictions,
)
from quant_gold.data.contracts import FeatureSpec, TargetSpec
from quant_gold.features.builders import FeatureBuilder
from quant_gold.models.targets import TargetBuilder
from quant_gold.pipelines.v01_pipeline import load_dataset_specs
from quant_gold.utils.sample_data import generate_sample_standard_frames


def test_generate_walk_forward_predictions_returns_positions() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec())
    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=5),
        required_feature_columns=[
            "return_1d",
            "log_return_1d",
            "momentum_5d",
            "momentum_20d",
            "rolling_mean_ratio_5",
            "rolling_mean_ratio_20",
            "rolling_vol_10d",
            "rolling_vol_20d",
        ],
    )

    predictions = generate_walk_forward_predictions(
        model_frame,
        WalkForwardConfig(
            model_name="logistic_regression",
            model_params={},
            feature_columns=[
                "return_1d",
                "log_return_1d",
                "momentum_5d",
                "momentum_20d",
                "rolling_mean_ratio_5",
                "rolling_mean_ratio_20",
                "rolling_vol_10d",
                "rolling_vol_20d",
            ],
            target_horizon_days=5,
            lookback_years=2,
            initial_train_years=1,
            retrain_frequency_days=21,
        ),
    )

    assert len(predictions) > 50
    assert {"predicted_direction", "signal", "position"}.issubset(predictions.columns)


def test_run_long_flat_backtest_returns_metrics() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec())
    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=5),
        required_feature_columns=["return_1d", "momentum_5d"],
    )
    predictions = generate_walk_forward_predictions(
        model_frame,
        WalkForwardConfig(
            model_name="logistic_regression",
            model_params={},
            feature_columns=["return_1d", "momentum_5d"],
            target_horizon_days=5,
            lookback_years=2,
            initial_train_years=1,
            retrain_frequency_days=21,
        ),
    )

    result = run_long_flat_backtest(predictions, transaction_cost_bps=5)
    assert "strategy_sharpe" in result.metrics
    assert "benchmark_total_return" in result.metrics


def test_build_horizon_aligned_position_uses_overlapping_average_for_multi_day_targets() -> None:
    signal = pd.Series([1, 0, 1, 1, 0, 1], dtype=float)
    position = _build_horizon_aligned_position(signal, horizon_days=3)

    expected = pd.Series([0.0, 1 / 3, 1 / 3, 2 / 3, 2 / 3, 2 / 3], dtype=float)
    pd.testing.assert_series_equal(position.reset_index(drop=True), expected, check_names=False)
