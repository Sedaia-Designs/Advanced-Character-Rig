"""Atomic JSON persistence helpers for extension-local data."""

import json
from pathlib import Path


def read_json(path: Path) -> dict:
    """Read a UTF-8 JSON file from disk."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict) -> None:
    """Atomically replace a UTF-8 JSON file with serialized data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=True, indent=4), encoding="utf-8")
    temporary.replace(path)
