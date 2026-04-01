from __future__ import annotations

from dataclasses import dataclass

from quant_gold.models.model_selection import ModelSpec, compare_classification_models
from quant_gold.models.splitters import SplitFrames


@dataclass(frozen=True)
class OptimizationResult:
    best_spec: ModelSpec
    rows: list[dict]


def generate_candidate_specs() -> list[ModelSpec]:
    specs: list[ModelSpec] = []
    for c_value in (0.03, 0.05, 0.1, 0.3, 1.0):
        specs.append(ModelSpec("logistic_regression", {"C": c_value}))
    for alpha in (1.0, 3.0, 10.0, 30.0, 100.0):
        specs.append(ModelSpec("ridge_classifier", {"alpha": alpha}))
    for max_depth, min_leaf in ((2, 40), (2, 80), (3, 40), (3, 80)):
        specs.append(ModelSpec("random_forest", {"max_depth": max_depth, "min_samples_leaf": min_leaf}))
    for n_estimators, learning_rate, max_depth in (
        (100, 0.02, 1),
        (100, 0.02, 2),
        (200, 0.02, 1),
        (200, 0.02, 2),
        (100, 0.05, 1),
    ):
        specs.append(
            ModelSpec(
                "gradient_boosting",
                {
                    "n_estimators": n_estimators,
                    "learning_rate": learning_rate,
                    "max_depth": max_depth,
                },
            )
        )
    return specs


def optimize_model_spec(
    split_frames: SplitFrames,
    feature_columns: list[str],
    overfit_penalty: float = 0.6,
) -> OptimizationResult:
    comparison_results = compare_classification_models(
        split_frames=split_frames,
        feature_columns=feature_columns,
        candidate_models=generate_candidate_specs(),
    )

    rows: list[dict] = []
    for result in comparison_results:
        train_accuracy = result.metrics_by_split["train"]["accuracy"]
        validation_accuracy = result.metrics_by_split["validation"]["accuracy"]
        test_accuracy = result.metrics_by_split["test"]["accuracy"]
        generalization_gap = max(train_accuracy - validation_accuracy, 0.0)
        objective_score = validation_accuracy - overfit_penalty * generalization_gap
        rows.append(
            {
                "model_name": result.model_name,
                "model_params": result.model_params,
                "model_label": ModelSpec(result.model_name, result.model_params).label,
                "train_accuracy": train_accuracy,
                "validation_accuracy": validation_accuracy,
                "test_accuracy": test_accuracy,
                "generalization_gap": generalization_gap,
                "objective_score": objective_score,
            }
        )

    ranked = sorted(rows, key=lambda row: (row["objective_score"], row["validation_accuracy"]), reverse=True)
    best = ranked[0]
    return OptimizationResult(
        best_spec=ModelSpec(model_name=best["model_name"], model_params=best["model_params"]),
        rows=ranked,
    )
