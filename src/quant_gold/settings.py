from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    project_root: Path
    alpha_vantage_api_key: str | None
    fred_api_key: str | None

    @property
    def data_raw_dir(self) -> Path:
        return self.project_root / "data" / "raw"

    @property
    def data_interim_dir(self) -> Path:
        return self.project_root / "data" / "interim"

    @property
    def data_processed_dir(self) -> Path:
        return self.project_root / "data" / "processed"

    @property
    def reports_dir(self) -> Path:
        return self.project_root / "reports" / "generated"

    def ensure_local_dirs(self) -> None:
        for directory in (
            self.data_raw_dir,
            self.data_interim_dir,
            self.data_processed_dir,
            self.reports_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> Settings:
        root = project_root or Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env", override=False)
        return cls(
            project_root=root,
            alpha_vantage_api_key=os.getenv("ALPHAVANTAGE_API_KEY"),
            fred_api_key=os.getenv("FRED_API_KEY"),
        )
