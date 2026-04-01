from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quant_gold.data.contracts import SplitSpec


@dataclass(frozen=True)
class SplitFrames:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


class Splitter:
    def split(self, model_frame: pd.DataFrame, split_spec: SplitSpec) -> SplitFrames:
        n_rows = len(model_frame)
        train_end = int(n_rows * split_spec.train_fraction)
        valid_end = train_end + int(n_rows * split_spec.validation_fraction)
        if train_end <= 0 or valid_end >= n_rows:
            raise ValueError("Split fractions produced empty train/validation/test segments.")
        train = model_frame.iloc[:train_end].copy()
        validation = model_frame.iloc[train_end:valid_end].copy()
        test = model_frame.iloc[valid_end:].copy()
        return SplitFrames(train=train, validation=validation, test=test)

