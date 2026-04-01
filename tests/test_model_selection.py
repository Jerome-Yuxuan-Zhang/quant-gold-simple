from pathlib import Path

from quant_gold.data.contracts import FeatureSpec, SplitSpec, TargetSpec
from quant_gold.features.builders import FeatureBuilder
from quant_gold.models.model_selection import compare_classification_models
from quant_gold.models.splitters import Splitter
from quant_gold.models.targets import TargetBuilder
from quant_gold.pipelines.v01_pipeline import load_dataset_specs
from quant_gold.utils.sample_data import generate_sample_standard_frames


def test_compare_classification_models_returns_multiple_results() -> None:
    dataset_specs = load_dataset_specs(project_root=Path(__file__).resolve().parents[1])
    standard_frames = generate_sample_standard_frames(dataset_specs)
    feature_frame = FeatureBuilder().build(standard_frames, FeatureSpec())
    model_frame = TargetBuilder().build(feature_frame, TargetSpec(forecast_horizon_days=5))
    split_frames = Splitter().split(model_frame, SplitSpec(train_fraction=0.6, validation_fraction=0.2))

    feature_columns = [
        "return_1d",
        "log_return_1d",
        "momentum_5d",
        "momentum_20d",
        "rolling_mean_ratio_5",
        "rolling_mean_ratio_20",
        "rolling_vol_10d",
        "rolling_vol_20d",
    ]
    results = compare_classification_models(
        split_frames=split_frames,
        feature_columns=feature_columns,
        candidate_models=["logistic_regression", "ridge_classifier"],
    )

    assert len(results) == 2
    assert results[0].metrics_by_split["train"]["accuracy"] >= 0.0
