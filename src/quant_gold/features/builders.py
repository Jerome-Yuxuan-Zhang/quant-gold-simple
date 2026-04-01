from __future__ import annotations

import numpy as np
import pandas as pd

from quant_gold.data.contracts import FeatureSpec, StandardFrame


class FeatureBuilder:
    def build(self, standard_frames: list[StandardFrame], feature_spec: FeatureSpec) -> pd.DataFrame:
        wide = self._assemble_wide_frame(standard_frames)
        wide = self._apply_exogenous_lag(wide, exogenous_lag_days=feature_spec.exogenous_lag_days)
        wide = self._fill_exogenous_gaps(wide)

        wide["return_1d"] = wide["gold_close"].pct_change()
        wide["log_return_1d"] = np.log(wide["gold_close"] / wide["gold_close"].shift(1))
        wide["momentum_5d"] = wide["gold_close"].pct_change(5)
        wide["momentum_20d"] = wide["gold_close"].pct_change(20)
        wide["rolling_mean_ratio_5"] = wide["gold_close"] / wide["gold_close"].rolling(5).mean() - 1.0
        wide["rolling_mean_ratio_20"] = wide["gold_close"] / wide["gold_close"].rolling(20).mean() - 1.0
        wide["rolling_vol_10d"] = wide["return_1d"].rolling(10).std()
        wide["rolling_vol_20d"] = wide["return_1d"].rolling(20).std()

        if {"silver_close", "gold_close"}.issubset(wide.columns):
            wide["silver_gold_ratio"] = wide["silver_close"] / wide["gold_close"]

        if {"yield_10y", "yield_2y"}.issubset(wide.columns):
            wide["yield_spread_10y_2y"] = wide["yield_10y"] - wide["yield_2y"]

        if {"yield_10y", "breakeven_proxy"}.issubset(wide.columns):
            wide["real_rate_gap"] = wide["yield_10y"] - wide["breakeven_proxy"]
        if "real_yield_proxy" in wide.columns:
            wide["real_rate_gap"] = wide["real_yield_proxy"]

        if "usd_proxy" in wide.columns:
            wide["usd_proxy_z20"] = self._zscore(wide["usd_proxy"], window=feature_spec.zscore_window)
        if "vix_proxy" in wide.columns:
            wide["vix_proxy_z20"] = self._zscore(wide["vix_proxy"], window=feature_spec.zscore_window)
        if "equity_proxy" in wide.columns:
            wide["equity_return_5d"] = wide["equity_proxy"].pct_change(5)
        if "oil_close" in wide.columns:
            wide["oil_return_5d"] = wide["oil_close"].pct_change(5)

        return wide.sort_values("date").reset_index(drop=True)

    def _assemble_wide_frame(self, standard_frames: list[StandardFrame]) -> pd.DataFrame:
        anchor = next((frame for frame in standard_frames if frame.dataset_spec.name == "gold_close"), None)
        if anchor is None:
            raise ValueError("FeatureBuilder requires `gold_close` as the master calendar.")

        merged = anchor.frame[["date", "value"]].rename(columns={"value": "gold_close"}).copy()
        merged = merged.sort_values("date").reset_index(drop=True)
        for standard_frame in standard_frames:
            if standard_frame.dataset_spec.name == "gold_close":
                continue
            frame = standard_frame.frame[["date", "value"]].rename(columns={"value": standard_frame.dataset_spec.name})
            merged = merged.merge(frame, on="date", how="left")
        return merged

    def _apply_exogenous_lag(self, frame: pd.DataFrame, exogenous_lag_days: int) -> pd.DataFrame:
        lagged = frame.copy()
        exogenous_columns = [column for column in lagged.columns if column not in {"date", "gold_close"}]
        lagged.loc[:, exogenous_columns] = lagged.loc[:, exogenous_columns].shift(exogenous_lag_days)
        return lagged

    def _fill_exogenous_gaps(self, frame: pd.DataFrame) -> pd.DataFrame:
        filled = frame.copy()
        exogenous_columns = [column for column in filled.columns if column not in {"date", "gold_close"}]
        filled.loc[:, exogenous_columns] = filled.loc[:, exogenous_columns].ffill(limit=5)
        return filled

    def _zscore(self, series: pd.Series, window: int) -> pd.Series:
        rolling_mean = series.rolling(window).mean()
        rolling_std = series.rolling(window).std()
        return (series - rolling_mean) / rolling_std
