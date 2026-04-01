import pandas as pd

from quant_gold.evaluation.metrics import evaluate_classification, evaluate_regression


def test_classification_metrics_return_expected_keys() -> None:
    metrics = evaluate_classification(
        y_true=pd.Series([1, 0, 1, 1]),
        y_pred=pd.Series([1, 0, 0, 1]),
    )
    assert set(metrics) == {"accuracy", "precision", "recall", "hit_ratio"}


def test_regression_metrics_return_expected_keys() -> None:
    metrics = evaluate_regression(
        y_true=pd.Series([0.1, 0.2, 0.05]),
        y_pred=pd.Series([0.11, 0.18, 0.04]),
    )
    assert set(metrics) == {"mae", "rmse"}

