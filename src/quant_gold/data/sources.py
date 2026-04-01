from __future__ import annotations

from datetime import datetime
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from quant_gold.data.base import DataSource
from quant_gold.data.cache import RawCache
from quant_gold.data.contracts import DatasetSpec, RawPayload, utc_now


class HttpDataSource(DataSource):
    def __init__(self, cache: RawCache, api_key: str | None) -> None:
        self.cache = cache
        self.api_key = api_key
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    def _get_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()


class AlphaVantageDataSource(HttpDataSource):
    base_url = "https://www.alphavantage.co/query"

    def fetch(self, dataset_spec: DatasetSpec) -> RawPayload:
        cached = self.cache.load(dataset_spec)
        if cached is not None:
            return RawPayload(
                dataset_spec=dataset_spec,
                raw_data=cached,
                fetched_at=datetime.fromisoformat(cached["fetched_at"]),
            )

        if not self.api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY is required for remote Alpha Vantage fetches.")

        params = {**dataset_spec.params, "apikey": self.api_key}
        payload = self._get_json(self.base_url, params=params)
        self._validate_payload(payload)
        wrapped = {
            "provider": "alpha_vantage",
            "dataset_name": dataset_spec.name,
            "remote_id": dataset_spec.remote_id,
            "fetched_at": utc_now().isoformat(),
            "payload": payload,
        }
        self.cache.save(dataset_spec, wrapped)
        return RawPayload(
            dataset_spec=dataset_spec,
            raw_data=wrapped,
            fetched_at=datetime.fromisoformat(wrapped["fetched_at"]),
        )

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        for key in ("Error Message", "Note", "Information"):
            if key in payload:
                raise ValueError(f"Alpha Vantage returned a non-data payload: {payload[key]}")


class FredDataSource(HttpDataSource):
    base_url = "https://api.stlouisfed.org/fred"

    def fetch(self, dataset_spec: DatasetSpec) -> RawPayload:
        cached = self.cache.load(dataset_spec)
        if cached is not None:
            return RawPayload(
                dataset_spec=dataset_spec,
                raw_data=cached,
                fetched_at=datetime.fromisoformat(cached["fetched_at"]),
            )

        if not self.api_key:
            raise ValueError("FRED_API_KEY is required for remote FRED fetches.")

        series_id = dataset_spec.params["series_id"]
        metadata = self._get_json(
            f"{self.base_url}/series",
            params={"series_id": series_id, "api_key": self.api_key, "file_type": "json"},
        )
        observations = self._get_json(
            f"{self.base_url}/series/observations",
            params={"series_id": series_id, "api_key": self.api_key, "file_type": "json"},
        )
        self._validate_payload(metadata)
        self._validate_payload(observations)

        wrapped = {
            "provider": "fred",
            "dataset_name": dataset_spec.name,
            "remote_id": dataset_spec.remote_id,
            "fetched_at": utc_now().isoformat(),
            "payload": {
                "series": metadata,
                "observations": observations,
            },
        }
        self.cache.save(dataset_spec, wrapped)
        return RawPayload(
            dataset_spec=dataset_spec,
            raw_data=wrapped,
            fetched_at=datetime.fromisoformat(wrapped["fetched_at"]),
        )

    @staticmethod
    def _validate_payload(payload: dict[str, Any]) -> None:
        if "error_message" in payload:
            raise ValueError(f"FRED returned an error payload: {payload['error_message']}")
