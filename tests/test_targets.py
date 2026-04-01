import pandas as pd

from quant_gold.data.contracts import TargetSpec
from quant_gold.models.targets import TargetBuilder


def test_target_builder_accumulates_future_returns_for_multi_day_horizon() -> None:
    feature_frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "return_1d": [0.01, -0.02, 0.03, 0.01, -0.01, 0.02],
        }
    )

    model_frame = TargetBuilder().build(feature_frame, TargetSpec(forecast_horizon_days=3))

    assert round(model_frame.loc[0, "target_return_1d"], 6) == 0.02
    assert model_frame.loc[0, "target_direction_1d"] == 1
    assert (model_frame["target_horizon_days"] == 3).all()


def test_target_builder_drops_only_required_feature_columns() -> None:
    feature_frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "return_1d": [0.01, -0.02, 0.03, 0.01, -0.01, 0.02],
            "feature_a": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "unused_feature": [None, None, None, None, None, None],
        }
    )

    model_frame = TargetBuilder().build(
        feature_frame,
        TargetSpec(forecast_horizon_days=1),
        required_feature_columns=["feature_a"],
    )

    assert len(model_frame) > 0
