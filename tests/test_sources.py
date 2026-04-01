from pathlib import Path

import pytest

from quant_gold.data.cache import RawCache
from quant_gold.data.contracts import DatasetSpec
from quant_gold.data.sources import AlphaVantageDataSource, FredDataSource


class AlphaVantageRateLimitedSource(AlphaVantageDataSource):
    def _get_json(self, url: str, params: dict[str, str]) -> dict[str, str]:
        return {"Note": "API call frequency is exceeded."}


class FredErrorSource(FredDataSource):
    def _get_json(self, url: str, params: dict[str, str]) -> dict[str, str]:
        return {"error_message": "Bad Request.  The value for variable api_key is not registered."}


def _dataset_spec(source: str, remote_id: str) -> DatasetSpec:
    return DatasetSpec(
        name="test_series",
        source=source,
        remote_id=remote_id,
        description="Test dataset",
        native_frequency="daily",
        unit="unit",
        params={"series_id": remote_id} if source == "fred" else {"function": "TIME_SERIES_DAILY"},
    )


def test_alpha_vantage_source_raises_on_rate_limit_payload(tmp_path: Path) -> None:
    source = AlphaVantageRateLimitedSource(cache=RawCache(tmp_path / "raw"), api_key="demo")

    with pytest.raises(ValueError, match="Alpha Vantage returned a non-data payload"):
        source.fetch(_dataset_spec("alpha_vantage", "GOLD"))


def test_fred_source_raises_on_error_payload(tmp_path: Path) -> None:
    source = FredErrorSource(cache=RawCache(tmp_path / "raw"), api_key="demo")

    with pytest.raises(ValueError, match="FRED returned an error payload"):
        source.fetch(_dataset_spec("fred", "DGS10"))
