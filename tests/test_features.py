from pathlib import Path

from quant_gold.data.contracts import FeatureSpec
from quant_gold.features.builders import FeatureBuilder
from quant_gold.pipelines.v01_pipeline import load_dataset_specs
from quant_gold.utils.sample_data import generate_sample_standard_frames


def test_feature_builder_creates_expected_columns() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec())

    expected = {
        "gold_close",
        "return_1d",
        "log_return_1d",
        "momentum_5d",
        "rolling_vol_20d",
        "silver_gold_ratio",
        "yield_spread_10y_2y",
        "usd_proxy_z20",
    }
    assert expected.issubset(feature_frame.columns)


def test_feature_builder_applies_exogenous_lag() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec(exogenous_lag_days=1))

    original_usd = next(frame.frame for frame in standard_frames if frame.dataset_spec.name == "usd_proxy")
    assert feature_frame.loc[1, "usd_proxy"] == original_usd.loc[0, "value"]


def test_feature_builder_anchors_to_gold_calendar() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    gold_frame = next(frame.frame for frame in standard_frames if frame.dataset_spec.name == "gold_close")

    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec())

    assert len(feature_frame) == len(gold_frame)
    assert feature_frame["date"].min() == gold_frame["date"].min()
    assert feature_frame["date"].max() == gold_frame["date"].max()
