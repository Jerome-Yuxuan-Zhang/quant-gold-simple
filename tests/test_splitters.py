import pandas as pd

from quant_gold.data.contracts import SplitSpec
from quant_gold.models.splitters import Splitter


def test_splitter_respects_time_order() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "target_direction_1d": [0, 1] * 5,
            "target_return_1d": [0.1] * 10,
        }
    )
    split_frames = Splitter().split(frame, SplitSpec(train_fraction=0.5, validation_fraction=0.2))

    assert split_frames.train["date"].max() < split_frames.validation["date"].min()
    assert split_frames.validation["date"].max() < split_frames.test["date"].min()
    assert len(split_frames.train) == 5

