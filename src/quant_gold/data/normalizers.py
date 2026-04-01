from __future__ import annotations

from typing import Any

import pandas as pd

from quant_gold.data.contracts import RawPayload, StandardFrame


class Normalizer:
    def normalize(self, raw_payload: RawPayload) -> StandardFrame:
        source = raw_payload.dataset_spec.source
        if source == "alpha_vantage":
            frame = self._normalize_alpha_vantage(raw_payload)
        elif source == "fred":
            frame = self._normalize_fred(raw_payload)
        else:
            raise ValueError(f"Unsupported source: {source}")
        return StandardFrame(dataset_spec=raw_payload.dataset_spec, frame=frame)

    def _normalize_alpha_vantage(self, raw_payload: RawPayload) -> pd.DataFrame:
        payload = raw_payload.raw_data["payload"]
        if "data" in payload and isinstance(payload["data"], list):
            frame = pd.DataFrame(payload["data"])
            if "value" not in frame.columns:
                if "price" in frame.columns:
                    frame = frame.rename(columns={"price": "value"})
                else:
                    numeric_candidate = next(
                        (column for column in frame.columns if column != "date"),
                        None,
                    )
                    if numeric_candidate is None:
                        raise ValueError("Could not infer numeric value column from Alpha Vantage payload.")
                    frame = frame.rename(columns={numeric_candidate: "value"})
        else:
            time_series_key = next((key for key in payload if "Time Series" in key), None)
            if time_series_key is None:
                raise ValueError("Could not find Alpha Vantage time-series payload.")
            records: list[dict[str, Any]] = []
            for date, values in payload[time_series_key].items():
                close_key = next((key for key in values if key.endswith("close")), None)
                if close_key is None:
                    raise ValueError("Could not find close field in Alpha Vantage payload.")
                records.append({"date": date, "value": values[close_key]})
            frame = pd.DataFrame(records)

        frame["date"] = pd.to_datetime(frame["date"])
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = frame.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
        frame["series_id"] = raw_payload.dataset_spec.name
        frame["source"] = raw_payload.dataset_spec.source
        frame["native_frequency"] = raw_payload.dataset_spec.native_frequency
        frame["unit"] = payload.get("unit", raw_payload.dataset_spec.unit)
        frame["last_updated"] = frame["date"].max().strftime("%Y-%m-%d")
        frame["description"] = raw_payload.dataset_spec.description
        return frame[
            [
                "date",
                "value",
                "series_id",
                "source",
                "native_frequency",
                "unit",
                "last_updated",
                "description",
            ]
        ]

    def _normalize_fred(self, raw_payload: RawPayload) -> pd.DataFrame:
        payload = raw_payload.raw_data["payload"]
        observations = payload["observations"]["observations"]
        frame = pd.DataFrame(observations)
        series_metadata = payload["series"]["seriess"][0]
        frame["date"] = pd.to_datetime(frame["date"])
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = frame.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
        frame["series_id"] = raw_payload.dataset_spec.name
        frame["source"] = raw_payload.dataset_spec.source
        frame["native_frequency"] = series_metadata.get("frequency_short", raw_payload.dataset_spec.native_frequency)
        frame["unit"] = series_metadata.get("units", raw_payload.dataset_spec.unit)
        frame["last_updated"] = series_metadata.get("last_updated", "")
        frame["description"] = series_metadata.get("title", raw_payload.dataset_spec.description)
        return frame[
            [
                "date",
                "value",
                "series_id",
                "source",
                "native_frequency",
                "unit",
                "last_updated",
                "description",
            ]
        ]
