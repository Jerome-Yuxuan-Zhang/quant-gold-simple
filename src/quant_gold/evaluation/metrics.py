from __future__ import annotations

import math

import pandas as pd
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error, precision_score, recall_score


def evaluate_classification(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "hit_ratio": float((y_true == y_pred).mean()),
    }


def evaluate_regression(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(math.sqrt(mse)),
    }

