"""SQLite connection factory used by every table set in `core.databases`.

Patterns:

- Builder: `SQLite` collects ``sqlite3.connect`` options through chained setters.
- Factory: `SQLite.connect()` and `SQLite.session()` create connections with
  those options, so callers never repeat them.
"""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from typing import Self


class SQLite:
    """
    Builder and Factory for SQLite connections that share one set of connection options.

    Every option mirrors a parameter of ``sqlite3.connect`` and starts at the
    same default, so ``SQLite(path).connect()`` behaves exactly like
    ``sqlite3.connect(path)``. Change an option with its setter. Each setter
    returns the factory, so calls can be chained.
    """

    def __init__(self, database: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        self.database: str | bytes | os.PathLike[str] | os.PathLike[bytes] = database
        self.timeout: float = 5.0
        self.detect_types: int = 0
        self.isolation_level: str | None = "DEFERRED"
        self.check_same_thread: bool = True
        self.factory: type[sqlite3.Connection] = sqlite3.Connection
        self.cached_statements: int = 128
        self.uri: bool = False
        self.autocommit: bool | int = sqlite3.LEGACY_TRANSACTION_CONTROL

    def set_timeout(self, timeout: float) -> Self:
        """
        Set how many seconds to wait for a locked database before raising.
        """
        self.timeout = timeout
        return self

    def set_detect_types(self, detect_types: int) -> Self:
        """
        Set the type detection flags (``sqlite3.PARSE_DECLTYPES``, ``sqlite3.PARSE_COLNAMES``).
        """
        self.detect_types = detect_types
        return self

    def set_isolation_level(self, isolation_level: str | None) -> Self:
        """
        Set the legacy transaction mode: ``"DEFERRED"``, ``"IMMEDIATE"``, ``"EXCLUSIVE"``, or ``None``.

        Ignored unless autocommit is ``sqlite3.LEGACY_TRANSACTION_CONTROL``.
        """
        self.isolation_level = isolation_level
        return self

    def set_check_same_thread(self, check_same_thread: bool) -> Self:
        """
        Set whether only the creating thread may use a connection.
        """
        self.check_same_thread = check_same_thread
        return self

    def set_factory(self, factory: type[sqlite3.Connection]) -> Self:
        """
        Set the ``sqlite3.Connection`` subclass to create connections with.
        """
        self.factory = factory
        return self

    def set_cached_statements(self, cached_statements: int) -> Self:
        """
        Set how many compiled statements each connection caches.
        """
        self.cached_statements = cached_statements
        return self

    def set_uri(self, uri: bool) -> Self:
        """
        Set whether the database is read as a ``file:`` URI.
        """
        self.uri = uri
        return self

    def set_autocommit(self, autocommit: bool | int) -> Self:
        """
        Set the transaction control: ``True``, ``False``, or ``sqlite3.LEGACY_TRANSACTION_CONTROL``.
        """
        self.autocommit = autocommit
        return self

    def connect(self) -> sqlite3.Connection:
        """
        Open a new connection using this factory's options.

        The caller owns the returned connection and must close it.
        """
        return sqlite3.connect(
            self.database,
            timeout=self.timeout,
            detect_types=self.detect_types,
            isolation_level=self.isolation_level,
            check_same_thread=self.check_same_thread,
            factory=self.factory,
            cached_statements=self.cached_statements,
            uri=self.uri,
            autocommit=self.autocommit,
        )

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        """
        Open a connection for the duration of a ``with`` block.

        The transaction commits when the block succeeds, rolls back when it
        raises, and the connection is always closed afterwards.
        """
        with closing(self.connect()) as conn, conn:
            yield conn
