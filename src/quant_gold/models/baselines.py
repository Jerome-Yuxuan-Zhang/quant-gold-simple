from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from quant_gold.evaluation.metrics import evaluate_classification, evaluate_regression
from quant_gold.models.splitters import SplitFrames


@dataclass(frozen=True)
class BaselineResults:
    classification_metrics: dict[str, dict[str, float]]
    regression_metrics: dict[str, dict[str, float]]
    feature_columns: list[str]
    classification_coefficients: dict[str, float]


def _clean_feature_columns(frame: pd.DataFrame, feature_columns: list[str]) -> list[str]:
    usable = [column for column in feature_columns if column in frame.columns]
    if not usable:
        raise ValueError("No configured feature columns were present in the model frame.")
    return usable


def run_baselines(split_frames: SplitFrames, feature_columns: list[str]) -> BaselineResults:
    feature_columns = _clean_feature_columns(split_frames.train, feature_columns)
    x_train = split_frames.train[feature_columns]
    y_train_cls = split_frames.train["target_direction_1d"]
    y_train_reg = split_frames.train["target_return_1d"]

    classifier = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=500)),
        ]
    )
    classifier.fit(x_train, y_train_cls)

    ridge = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0)),
        ]
    )
    ridge.fit(x_train, y_train_reg)

    classification_metrics: dict[str, dict[str, float]] = {}
    regression_metrics: dict[str, dict[str, float]] = {}

    for split_name, split_frame in {
        "train": split_frames.train,
        "validation": split_frames.validation,
        "test": split_frames.test,
    }.items():
        x_split = split_frame[feature_columns]
        classification_metrics[split_name] = evaluate_classification(
            y_true=split_frame["target_direction_1d"],
            y_pred=classifier.predict(x_split),
        )
        regression_metrics[split_name] = evaluate_regression(
            y_true=split_frame["target_return_1d"],
            y_pred=ridge.predict(x_split),
        )

    previous_return = split_frames.test["return_1d"].shift(1).fillna(0.0)
    naive_direction = (previous_return > 0).astype(int)
    classification_metrics["test_naive_direction"] = evaluate_classification(
        y_true=split_frames.test["target_direction_1d"],
        y_pred=naive_direction,
    )

    return BaselineResults(
        classification_metrics=classification_metrics,
        regression_metrics=regression_metrics,
        feature_columns=feature_columns,
        classification_coefficients={
            column: float(value)
            for column, value in zip(feature_columns, classifier.named_steps["model"].coef_[0], strict=False)
        },
    )
