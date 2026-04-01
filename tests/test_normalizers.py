
from quant_gold.data.contracts import DatasetSpec, RawPayload, utc_now
from quant_gold.data.normalizers import Normalizer


def test_alpha_vantage_normalizer_handles_data_list_payload() -> None:
    spec = DatasetSpec(
        name="gold_close",
        source="alpha_vantage",
        remote_id="GOLD",
        description="gold",
        native_frequency="daily",
        unit="USD",
        params={},
    )
    payload = RawPayload(
        dataset_spec=spec,
        fetched_at=utc_now(),
        raw_data={
            "payload": {
                "unit": "USD",
                "data": [
                    {"date": "2024-01-02", "value": "2050.0"},
                    {"date": "2024-01-03", "value": "2060.0"}
                ]
            }
        },
    )

    normalized = Normalizer().normalize(payload)
    assert list(normalized.frame.columns) == [
        "date",
        "value",
        "series_id",
        "source",
        "native_frequency",
        "unit",
        "last_updated",
        "description",
    ]
    assert normalized.frame["value"].tolist() == [2050.0, 2060.0]


def test_alpha_vantage_normalizer_handles_price_field_payload() -> None:
    spec = DatasetSpec(
        name="gold_close",
        source="alpha_vantage",
        remote_id="GOLD",
        description="gold",
        native_frequency="daily",
        unit="USD",
        params={},
    )
    payload = RawPayload(
        dataset_spec=spec,
        fetched_at=utc_now(),
        raw_data={
            "payload": {
                "nominal": "USD",
                "data": [
                    {"date": "2024-01-02", "price": "2050.0"},
                    {"date": "2024-01-03", "price": "2060.0"}
                ]
            }
        },
    )

    normalized = Normalizer().normalize(payload)
    assert normalized.frame["value"].tolist() == [2050.0, 2060.0]


def test_fred_normalizer_drops_missing_observations() -> None:
    spec = DatasetSpec(
        name="yield_10y",
        source="fred",
        remote_id="DGS10",
        description="yield",
        native_frequency="daily",
        unit="Percent",
        params={"series_id": "DGS10"},
    )
    payload = RawPayload(
        dataset_spec=spec,
        fetched_at=utc_now(),
        raw_data={
            "payload": {
                "series": {
                    "seriess": [
                        {
                            "title": "Ten year yield",
                            "units": "Percent",
                            "frequency_short": "D",
                            "last_updated": "2026-03-26",
                        }
                    ]
                },
                "observations": {
                    "observations": [
                        {"date": "2024-01-02", "value": "."},
                        {"date": "2024-01-03", "value": "4.12"},
                    ]
                },
            }
        },
    )

    normalized = Normalizer().normalize(payload)
    assert len(normalized.frame) == 1
    assert float(normalized.frame.loc[0, "value"]) == 4.12
