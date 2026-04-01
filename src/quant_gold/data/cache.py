from __future__ import annotations

from pathlib import Path

from quant_gold.data.contracts import DatasetSpec
from quant_gold.utils.io import read_json, write_json


class RawCache:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, dataset_spec: DatasetSpec) -> Path:
        return self.root / f"{dataset_spec.cache_key()}.json"

    def load(self, dataset_spec: DatasetSpec) -> dict | None:
        path = self.path_for(dataset_spec)
        if not path.exists():
            return None
        return read_json(path)

    def save(self, dataset_spec: DatasetSpec, payload: dict) -> Path:
        path = self.path_for(dataset_spec)
        write_json(path, payload)
        return path
