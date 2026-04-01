from __future__ import annotations

from abc import ABC, abstractmethod

from quant_gold.data.contracts import DatasetSpec, RawPayload


class DataSource(ABC):
    @abstractmethod
    def fetch(self, dataset_spec: DatasetSpec) -> RawPayload:
        raise NotImplementedError

