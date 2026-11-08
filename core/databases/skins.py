"""SQLite storage for the Skin Manager: players, their skins, and their capes.

The schema follows the per-player JSON files written by the legacy skin
manager (``playerdata/<name>/<name>_Data.json``)::

    {
        "UUID": "...", "NAME": "...",
        "SKINS": [{"index": 0, "path": "...", "hash": "...", "model": "0"}],
        "CAPES": [{"index": 0, "path": "...", "hash": "...", "exists": true}]
    }

Each JSON file becomes one ``skin_players`` row, and each ``SKINS`` or
``CAPES`` entry becomes one ``skin_skins`` or ``skin_capes`` row. Two things
change from the JSON format:

- ``model`` is stored as ``"classic"`` or ``"slim"`` instead of ``"0"`` or ``"1"``.
- A cape entry with ``"exists": false`` is not stored. No cape row means no cape.

The tables share the extension's database file with other features, so every
table name starts with ``skin_``.

This module never opens the database itself. Operators open a session with
``preferences.access.db_session()`` and pass the connection in::

    with db_session() as conn:
        skins = SkinDatabase(conn)
        skins.create_schema()
        player = skins.upsert_player(uuid, name)

Texture paths are stored as given. Store them relative to the player data
folder, and resolve them with ``Path(player_data_dir) / skin.path``. A legacy
absolute path still resolves correctly, because joining an absolute path
returns it unchanged.

Patterns:

- Facade: `SkinDatabase` is the only API the Skin Manager uses for storage.
- Adapter: the `_Table` row adapters turn rows into `Player`, `Skin`, and
  `Cape` records, and `parse_legacy` turns legacy JSON into a `LegacyPlayer`.
"""

import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .schema import apply_schema, schema_version

SCHEMA_VERSION = 1

# Key of this module's row in the shared `schema_versions` table.
SCHEMA_NAME = "skin_manager"

# Idempotent statements that create the Skin Manager tables.
SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS skin_players (
        uuid       TEXT PRIMARY KEY CHECK (length(uuid) = 32),
        name       TEXT NOT NULL COLLATE NOCASE,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS skin_players_name ON skin_players (name)",
    """
    CREATE TABLE IF NOT EXISTS skin_skins (
        player_uuid TEXT NOT NULL REFERENCES skin_players (uuid) ON DELETE CASCADE,
        idx         INTEGER NOT NULL CHECK (idx >= 0),
        hash        TEXT NOT NULL,
        path        TEXT NOT NULL,
        model       TEXT NOT NULL CHECK (model IN ('classic', 'slim')),
        added_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (player_uuid, idx)
    )
    """,
    "CREATE INDEX IF NOT EXISTS skin_skins_hash ON skin_skins (player_uuid, hash)",
    """
    CREATE TABLE IF NOT EXISTS skin_capes (
        player_uuid TEXT NOT NULL REFERENCES skin_players (uuid) ON DELETE CASCADE,
        idx         INTEGER NOT NULL CHECK (idx >= 0),
        hash        TEXT NOT NULL,
        path        TEXT NOT NULL,
        added_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (player_uuid, idx)
    )
    """,
    "CREATE INDEX IF NOT EXISTS skin_capes_hash ON skin_capes (player_uuid, hash)",
)


class SkinModel(StrEnum):
    """The arm width a skin is drawn for, named as in Mojang's texture metadata."""

    CLASSIC = "classic"  # Legacy model "0": 4 px wide arms.
    SLIM = "slim"  # Legacy model "1": 3 px wide arms.


class LegacyFormatError(ValueError):
    """Raised when legacy player JSON is missing fields or has the wrong types."""


@dataclass(frozen=True, slots=True)
class Player:
    """One Minecraft Java Edition profile."""

    uuid: str
    name: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class Skin:
    """One downloaded skin texture. `index` counts up from 0 per player."""

    player_uuid: str
    index: int
    hash: str
    path: str
    model: SkinModel
    added_at: str


@dataclass(frozen=True, slots=True)
class Cape:
    """One downloaded cape texture. `index` counts up from 0 per player."""

    player_uuid: str
    index: int
    hash: str
    path: str
    added_at: str


def normalize_uuid(uuid: str) -> str:
    """Return `uuid` as 32 lowercase hex digits, the form Mojang's API uses.

    Accepts the dashed form too. Raises `ValueError` for anything else.
    """
    compact = uuid.replace("-", "").lower()
    if len(compact) != 32 or any(c not in "0123456789abcdef" for c in compact):
        raise ValueError(f"Not a Minecraft UUID: {uuid!r}")
    return compact


# region Row adapters


@dataclass(frozen=True, slots=True)
class _Table:
    """A table and the Adapter that turns one of its rows into a record.

    Skins and capes share their query shapes, so `SkinDatabase` writes each
    query once and takes the `_Table` to run it on.
    """

    name: str
    columns: str
    from_row: Callable[[sqlite3.Row | tuple], Any]


def _skin_from_row(row: sqlite3.Row | tuple) -> Skin:
    uuid, index, hash_, path, model, added_at = row
    return Skin(uuid, index, hash_, path, SkinModel(model), added_at)


_PLAYERS = _Table("skin_players", "uuid, name, created_at, updated_at", lambda row: Player(*row))
_SKINS = _Table("skin_skins", "player_uuid, idx, hash, path, model, added_at", _skin_from_row)
_CAPES = _Table("skin_capes", "player_uuid, idx, hash, path, added_at", lambda row: Cape(*row))

# endregion


class SkinDatabase:
    """Facade over the Skin Manager tables, used through an open SQLite connection.

    Callers work with `Player`, `Skin`, and `Cape` records and never write SQL.
    The caller owns the connection and its transaction. Every method runs
    inside whatever transaction is open, so several calls inside one
    ``db_session()`` block commit or roll back together.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        # Foreign keys are off by default and must be enabled per connection.
        # The pragma is ignored inside a transaction, so set it before any write.
        conn.execute("PRAGMA foreign_keys = ON")

    # region Schema

    def create_schema(self) -> None:
        """Create the tables if they are missing and record the schema version.

        Raises `core.databases.schema.SchemaVersionError` if the database was
        written by a newer version of this module, so old code never writes to
        a newer layout.
        """
        apply_schema(self.conn, SCHEMA_NAME, SCHEMA_VERSION, SCHEMA)

    def schema_version(self) -> int | None:
        """Return the stored schema version, or `None` if the schema was never created."""
        return schema_version(self.conn, SCHEMA_NAME)

    # endregion
    # region Players

    def upsert_player(self, uuid: str, name: str) -> Player:
        """Add a player, or update the stored name of an existing one.

        Players can change their name, so the UUID is the key and the name is
        refreshed on every call.
        """
        if not name:
            raise ValueError("name must be a non-empty string")
        row = self.conn.execute(
            f"""
            INSERT INTO skin_players (uuid, name) VALUES (?, ?)
            ON CONFLICT (uuid) DO UPDATE SET
                name = excluded.name,
                updated_at = CASE WHEN name = excluded.name
                                  THEN updated_at ELSE CURRENT_TIMESTAMP END
            RETURNING {_PLAYERS.columns}
            """,
            (normalize_uuid(uuid), name),
        ).fetchone()
        return _PLAYERS.from_row(row)

    def player(self, uuid: str) -> Player | None:
        """Return the player with `uuid`, or `None`."""
        return self._one(_PLAYERS, "uuid = ?", (normalize_uuid(uuid),))

    def find_player(self, name: str) -> Player | None:
        """Return the player stored under `name`, ignoring case, or `None`.

        A name can pass from one player to another after a rename, so two
        rows may share it. The most recently updated row wins.
        """
        return self._one(_PLAYERS, "name = ?", (name,), "updated_at DESC, rowid DESC")

    def players(self) -> list[Player]:
        """Return every stored player, sorted by name."""
        rows = self.conn.execute(f"SELECT {_PLAYERS.columns} FROM skin_players ORDER BY name")
        return [_PLAYERS.from_row(row) for row in rows]

    def delete_player(self, uuid: str) -> bool:
        """Delete a player with all their skins and capes. Return whether it existed.

        Only rows are removed. Deleting the texture files is the caller's job.
        """
        cursor = self.conn.execute(
            "DELETE FROM skin_players WHERE uuid = ?", (normalize_uuid(uuid),)
        )
        return cursor.rowcount > 0

    # endregion
    # region Skins

    def add_skin(self, uuid: str, hash: str, path: str, model: SkinModel,
                 index: int | None = None) -> Skin:
        """Store a skin for an existing player and return it.

        `index` defaults to one past the player's newest skin, starting at 0.
        Raises `sqlite3.IntegrityError` if the player does not exist or
        `index` is already taken.
        """
        return self._add(_SKINS, uuid, index, hash=hash, path=path, model=SkinModel(model).value)

    def skins(self, uuid: str) -> list[Skin]:
        """Return a player's skins, oldest first."""
        return self._all(_SKINS, uuid)

    def skin(self, uuid: str, index: int) -> Skin | None:
        """Return the skin at `index`, or `None`. An index of -1 returns the newest skin."""
        if index == -1:
            return self.latest_skin(uuid)
        return self._one(_SKINS, "player_uuid = ? AND idx = ?", (normalize_uuid(uuid), index))

    def latest_skin(self, uuid: str) -> Skin | None:
        """Return a player's newest skin, or `None` if they have none."""
        return self._latest(_SKINS, uuid)

    def find_skin(self, uuid: str, hash: str) -> Skin | None:
        """Return the newest of a player's skins with texture `hash`, or `None`.

        Use this to skip downloading a texture that is already stored.
        """
        return self._find(_SKINS, uuid, hash)

    # endregion
    # region Capes

    def add_cape(self, uuid: str, hash: str, path: str, index: int | None = None) -> Cape:
        """Store a cape for an existing player and return it. See `add_skin`."""
        return self._add(_CAPES, uuid, index, hash=hash, path=path)

    def capes(self, uuid: str) -> list[Cape]:
        """Return a player's capes, oldest first."""
        return self._all(_CAPES, uuid)

    def latest_cape(self, uuid: str) -> Cape | None:
        """Return a player's newest cape, or `None` if they have none."""
        return self._latest(_CAPES, uuid)

    def find_cape(self, uuid: str, hash: str) -> Cape | None:
        """Return the newest of a player's capes with texture `hash`, or `None`."""
        return self._find(_CAPES, uuid, hash)

    # endregion
    # region Legacy import

    def import_legacy(self, data: Mapping[str, Any]) -> Player:
        """Store one parsed legacy ``<name>_Data.json`` file and return its player.

        Existing skins and capes of that player are replaced, so importing the
        same file twice gives the same result. Entries keep their legacy index.
        Raises `LegacyFormatError` if `data` does not have the legacy layout;
        nothing is written in that case.
        """
        legacy = parse_legacy(data)
        player = self.upsert_player(legacy.uuid, legacy.name)
        for table in (_SKINS, _CAPES):
            self.conn.execute(f"DELETE FROM {table.name} WHERE player_uuid = ?", (player.uuid,))
        for skin in legacy.skins:
            self.add_skin(player.uuid, skin.hash, skin.path, skin.model, index=skin.index)
        for cape in legacy.capes:
            self.add_cape(player.uuid, cape.hash, cape.path, index=cape.index)
        return player

    # endregion
    # region Shared queries
    # Table and column names come only from the module's `_Table` constants,
    # never from arguments, so formatting them into SQL is safe. Values are
    # always bound as parameters.

    def _one(self, table: _Table, where: str, params: tuple, order: str = "") -> Any:
        """Return the first row of `table` matching `where` as a record, or `None`."""
        order_by = f"ORDER BY {order}" if order else ""
        row = self.conn.execute(
            f"SELECT {table.columns} FROM {table.name} WHERE {where} {order_by} LIMIT 1",
            params,
        ).fetchone()
        return table.from_row(row) if row else None

    def _all(self, table: _Table, uuid: str) -> list:
        """Return every texture of a player in `table`, oldest first."""
        rows = self.conn.execute(
            f"SELECT {table.columns} FROM {table.name} WHERE player_uuid = ? ORDER BY idx",
            (normalize_uuid(uuid),),
        )
        return [table.from_row(row) for row in rows]

    def _latest(self, table: _Table, uuid: str) -> Any:
        """Return a player's newest texture in `table`, or `None`."""
        return self._one(table, "player_uuid = ?", (normalize_uuid(uuid),), "idx DESC")

    def _find(self, table: _Table, uuid: str, hash: str) -> Any:
        """Return a player's newest texture in `table` with `hash`, or `None`."""
        return self._one(
            table, "player_uuid = ? AND hash = ?", (normalize_uuid(uuid), hash), "idx DESC"
        )

    def _add(self, table: _Table, uuid: str, index: int | None, **values: str) -> Any:
        """Insert a texture row and return it as a record.

        `index` defaults to one past the player's newest entry in `table`.
        The default is computed in the same statement as the insert, so it
        cannot race with another insert.
        """
        names = ", ".join(values)
        placeholders = ", ".join(f":{name}" for name in values)
        row = self.conn.execute(
            f"""
            INSERT INTO {table.name} (player_uuid, idx, {names})
            SELECT :uuid, coalesce(:index, (SELECT max(idx) + 1 FROM {table.name}
                                             WHERE player_uuid = :uuid), 0), {placeholders}
            RETURNING {table.columns}
            """,
            {"uuid": normalize_uuid(uuid), "index": index, **values},
        ).fetchone()
        return table.from_row(row)

    # endregion


# region Legacy adapter


@dataclass(frozen=True, slots=True)
class LegacySkin:
    """One validated ``SKINS`` entry of a legacy player file."""

    index: int
    hash: str
    path: str
    model: SkinModel


@dataclass(frozen=True, slots=True)
class LegacyCape:
    """One validated ``CAPES`` entry of a legacy player file that has a cape."""

    index: int
    hash: str
    path: str


@dataclass(frozen=True, slots=True)
class LegacyPlayer:
    """A validated legacy ``<name>_Data.json`` file."""

    uuid: str
    name: str
    skins: tuple[LegacySkin, ...]
    capes: tuple[LegacyCape, ...]


def parse_legacy(data: Mapping[str, Any]) -> LegacyPlayer:
    """Adapt a parsed legacy player JSON file into a `LegacyPlayer`, without a database.

    Legacy ``model`` strings become `SkinModel` members, and cape entries
    marked ``"exists": false`` or with an empty path are dropped.
    Raises `LegacyFormatError` for a missing field or a wrong type.
    """

    def field(entry: Mapping[str, Any], key: str, kind: type, where: str):
        value = entry.get(key) if isinstance(entry, Mapping) else None
        # `bool` is a subclass of `int`, so reject it explicitly for indexes.
        if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
            raise LegacyFormatError(f"{where}: '{key}' must be {kind.__name__}")
        return value

    try:
        uuid = normalize_uuid(field(data, "UUID", str, "player"))
    except ValueError as error:
        if isinstance(error, LegacyFormatError):
            raise
        raise LegacyFormatError(f"player: {error}") from None
    name = field(data, "NAME", str, "player")
    if not name:
        raise LegacyFormatError("player: 'NAME' must not be empty")

    skins = []
    for i, entry in enumerate(field(data, "SKINS", list, "player")):
        where = f"SKINS[{i}]"
        model = field(entry, "model", str, where)
        if model not in ("0", "1"):
            raise LegacyFormatError(f"{where}: 'model' must be \"0\" or \"1\"")
        skins.append(LegacySkin(
            field(entry, "index", int, where),
            field(entry, "hash", str, where),
            field(entry, "path", str, where),
            SkinModel.SLIM if model == "1" else SkinModel.CLASSIC,
        ))

    capes = []
    # A player without a cape still had a CAPES list, but tolerate it missing.
    cape_entries = field(data, "CAPES", list, "player") if "CAPES" in data else []
    for i, entry in enumerate(cape_entries):
        where = f"CAPES[{i}]"
        if not field(entry, "exists", bool, where):
            continue
        path = field(entry, "path", str, where)
        if path:
            capes.append(LegacyCape(
                field(entry, "index", int, where), field(entry, "hash", str, where), path
            ))

    for kind, entries in (("SKINS", skins), ("CAPES", capes)):
        indexes = [entry.index for entry in entries]
        if any(index < 0 for index in indexes):
            raise LegacyFormatError(f"{kind}: indexes must not be negative")
        if len(set(indexes)) != len(indexes):
            raise LegacyFormatError(f"{kind}: indexes must be unique")

    return LegacyPlayer(uuid, name, tuple(skins), tuple(capes))


# endregion
