"""Local persistence for downloaded player data."""

from pathlib import Path

from ...core.storage import read_json, write_json
from .constants import PLAYER_DATA_SUFFIX


def player_dir(root: Path, username: str) -> Path:
    """Return the storage directory assigned to a player name."""
    return root / username


def player_file(root: Path, username: str) -> Path:
    """Return the player metadata JSON path within the player's directory."""
    return player_dir(root, username) / f"{username}{PLAYER_DATA_SUFFIX}"


def exists(root: Path, username: str) -> bool:
    """Check whether saved metadata exists for a player."""
    return player_file(root, username).is_file()


def load(root: Path, username: str) -> dict:
    """Load a player's saved metadata from JSON."""
    return read_json(player_file(root, username))


def save(root: Path, username: str, data: dict) -> None:
    """Persist player metadata using an atomic JSON replacement."""
    write_json(player_file(root, username), data)
