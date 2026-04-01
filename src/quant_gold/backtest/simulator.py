from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    daily_frame: pd.DataFrame
    metrics: dict[str, float]


def run_long_flat_backtest(prediction_frame: pd.DataFrame, transaction_cost_bps: float) -> BacktestResult:
    frame = prediction_frame.sort_values("date").reset_index(drop=True).copy()
    frame["turnover"] = frame["position"].diff().abs().fillna(frame["position"].abs())
    frame["transaction_cost"] = frame["turnover"] * (transaction_cost_bps / 10000.0)
    frame["strategy_return"] = frame["position"] * frame["return_1d"] - frame["transaction_cost"]
    frame["benchmark_return"] = frame["return_1d"]
    frame["strategy_equity"] = (1.0 + frame["strategy_return"]).cumprod()
    frame["benchmark_equity"] = (1.0 + frame["benchmark_return"]).cumprod()

    strategy_ann_return = _annualized_return(frame["strategy_equity"])
    benchmark_ann_return = _annualized_return(frame["benchmark_equity"])
    strategy_ann_vol = float(frame["strategy_return"].std() * math.sqrt(252))
    benchmark_ann_vol = float(frame["benchmark_return"].std() * math.sqrt(252))
    strategy_sharpe = strategy_ann_return / strategy_ann_vol if strategy_ann_vol > 0 else 0.0
    benchmark_sharpe = benchmark_ann_return / benchmark_ann_vol if benchmark_ann_vol > 0 else 0.0

    metrics = {
        "strategy_total_return": float(frame["strategy_equity"].iloc[-1] - 1.0),
        "benchmark_total_return": float(frame["benchmark_equity"].iloc[-1] - 1.0),
        "strategy_annualized_return": strategy_ann_return,
        "benchmark_annualized_return": benchmark_ann_return,
        "strategy_annualized_volatility": strategy_ann_vol,
        "benchmark_annualized_volatility": benchmark_ann_vol,
        "strategy_sharpe": float(strategy_sharpe),
        "benchmark_sharpe": float(benchmark_sharpe),
        "strategy_max_drawdown": float(_max_drawdown(frame["strategy_equity"])),
        "benchmark_max_drawdown": float(_max_drawdown(frame["benchmark_equity"])),
        "average_position": float(frame["position"].mean()),
        "annualized_turnover": float(frame["turnover"].mean() * 252),
    }
    return BacktestResult(daily_frame=frame, metrics=metrics)


def _annualized_return(equity_curve: pd.Series) -> float:
    if len(equity_curve) < 2:
        return 0.0
    total_return = float(equity_curve.iloc[-1])
    years = len(equity_curve) / 252.0
    if years <= 0 or total_return <= 0:
        return 0.0
    return float(total_return ** (1.0 / years) - 1.0)


def _max_drawdown(equity_curve: pd.Series) -> float:
    running_max = equity_curve.cummax()
    drawdown = equity_curve / running_max - 1.0
    return float(drawdown.min())
