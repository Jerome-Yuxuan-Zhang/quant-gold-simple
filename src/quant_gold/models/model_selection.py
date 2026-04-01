from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from quant_gold.evaluation.metrics import evaluate_classification
from quant_gold.models.splitters import SplitFrames


@dataclass(frozen=True)
class ModelComparisonResult:
    model_name: str
    model_params: dict[str, Any]
    feature_columns: list[str]
    metrics_by_split: dict[str, dict[str, float]]


@dataclass(frozen=True)
class ModelSpec:
    model_name: str
    model_params: dict[str, Any]

    @property
    def label(self) -> str:
        if not self.model_params:
            return self.model_name
        params = ",".join(f"{key}={value}" for key, value in sorted(self.model_params.items()))
        return f"{self.model_name}({params})"


def build_classifier(model_name: str, model_params: dict[str, Any] | None = None):
    model_params = model_params or {}
    if model_name == "logistic_regression":
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=2000, **model_params)),
            ]
        )
    if model_name == "ridge_classifier":
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", RidgeClassifier(**model_params)),
            ]
        )
    if model_name == "random_forest":
        params = {
            "n_estimators": 300,
            "max_depth": 5,
            "min_samples_leaf": 10,
            "random_state": 42,
        }
        params.update(model_params)
        return RandomForestClassifier(**params)
    if model_name == "gradient_boosting":
        params = {
            "n_estimators": 200,
            "learning_rate": 0.05,
            "max_depth": 2,
            "random_state": 42,
        }
        params.update(model_params)
        return GradientBoostingClassifier(**params)
    raise ValueError(f"Unsupported model name: {model_name}")


def compare_classification_models(
    split_frames: SplitFrames,
    feature_columns: list[str],
    candidate_models: list[str] | list[ModelSpec],
) -> list[ModelComparisonResult]:
    x_train = split_frames.train[feature_columns]
    y_train = split_frames.train["target_direction_1d"]

    results: list[ModelComparisonResult] = []
    for candidate in candidate_models:
        if isinstance(candidate, str):
            spec = ModelSpec(model_name=candidate, model_params={})
        else:
            spec = candidate
        model = build_classifier(spec.model_name, spec.model_params)
        model.fit(x_train, y_train)

        metrics_by_split: dict[str, dict[str, float]] = {}
        for split_name, split_frame in {
            "train": split_frames.train,
            "validation": split_frames.validation,
            "test": split_frames.test,
        }.items():
            predictions = model.predict(split_frame[feature_columns])
            metrics_by_split[split_name] = evaluate_classification(
                y_true=split_frame["target_direction_1d"],
                y_pred=pd.Series(predictions, index=split_frame.index),
            )

        results.append(
            ModelComparisonResult(
                model_name=spec.model_name,
                model_params=spec.model_params,
                feature_columns=feature_columns,
                metrics_by_split=metrics_by_split,
            )
        )
    return results
