"""Schema versioning shared by every table set in the extension's database.

Each feature (skins now, rigs later) owns a set of tables and records its own
schema version as one row of ``schema_versions``, keyed by the feature's
schema name. Features upgrade independently, and an older extension never
writes to tables laid out by a newer one.

Pattern: none. These are two stateless functions over a connection that every
table-set Facade calls; wrapping them in a class would add a layer without
adding behaviour.
"""

import sqlite3
from collections.abc import Iterable

_VERSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_versions (
    name    TEXT PRIMARY KEY,
    version INTEGER NOT NULL
)
"""


class SchemaVersionError(RuntimeError):
    """Raised when the database was written by a newer schema than this code knows."""


def schema_version(conn: sqlite3.Connection, name: str) -> int | None:
    """Return the recorded version of schema `name`, or `None` if it was never created."""
    try:
        row = conn.execute(
            "SELECT version FROM schema_versions WHERE name = ?", (name,)
        ).fetchone()
    except sqlite3.OperationalError:  # `schema_versions` does not exist yet.
        return None
    return row[0] if row else None


def apply_schema(conn: sqlite3.Connection, name: str, version: int,
                 statements: Iterable[str]) -> None:
    """Create schema `name` if it is missing and record it as `version`.

    `statements` must be idempotent (``CREATE ... IF NOT EXISTS``), because
    they run every time. Each runs on its own with ``execute``, since
    ``executescript`` would commit the caller's open transaction.

    Raises `SchemaVersionError` if the database already holds a newer version
    of `name`. When a feature ships version 2, add its migration here, keyed
    on the version found.
    """
    conn.execute(_VERSIONS_TABLE)
    found = schema_version(conn, name)
    if found is not None and found > version:
        raise SchemaVersionError(
            f"The '{name}' tables use schema {found}, but this version of the "
            f"extension only supports up to {version}. Update the extension."
        )

    for statement in statements:
        conn.execute(statement)

    if found is None:
        conn.execute(
            "INSERT INTO schema_versions (name, version) VALUES (?, ?)", (name, version)
        )
