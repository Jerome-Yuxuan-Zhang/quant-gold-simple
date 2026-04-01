from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def write_markdown(path: Path, content: str) -> None:
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")


def write_dataframe_csv(path: Path, frame: pd.DataFrame) -> None:
    ensure_directory(path.parent)
    frame.to_csv(path, index=False)


def render_markdown_table(table: pd.Series | pd.DataFrame, *, index: bool = True) -> str:
    """Render a markdown table with a plain-text fallback when tabulate is unavailable."""
    try:
        return table.to_markdown(index=index)
    except ImportError:
        if isinstance(table, pd.Series):
            rendered = table.to_string()
        else:
            rendered = table.to_string(index=index)
        return f"```text\n{rendered}\n```"
