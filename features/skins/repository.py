"""Local persistence for downloaded player data."""

from pathlib import Path

from ...core.storage import read_json, write_json
from .constants import PLAYER_DATA_SUFFIX


def player_dir(root: Path, username: str) -> Path:
    return root / username


def player_file(root: Path, username: str) -> Path:
    return player_dir(root, username) / f"{username}{PLAYER_DATA_SUFFIX}"


def exists(root: Path, username: str) -> bool:
    return player_file(root, username).is_file()


def load(root: Path, username: str) -> dict:
    return read_json(player_file(root, username))


def save(root: Path, username: str, data: dict) -> None:
    write_json(player_file(root, username), data)
