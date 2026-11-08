"""Blender-free tests for `core.databases.schema`, run against in-memory SQLite.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases.schema import SchemaVersionError, apply_schema, schema_version  # noqa: E402

TABLE = ("CREATE TABLE IF NOT EXISTS demo_items (id INTEGER PRIMARY KEY)",)


class ApplySchemaTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)

    def test_unknown_schema_has_no_version(self):
        self.assertIsNone(schema_version(self.conn, "demo"))

    def test_creates_tables_and_records_version(self):
        apply_schema(self.conn, "demo", 1, TABLE)
        self.assertEqual(schema_version(self.conn, "demo"), 1)
        self.conn.execute("INSERT INTO demo_items DEFAULT VALUES")

    def test_features_are_versioned_independently(self):
        apply_schema(self.conn, "demo", 1, TABLE)
        apply_schema(self.conn, "other", 3, ())
        self.assertEqual(schema_version(self.conn, "demo"), 1)
        self.assertEqual(schema_version(self.conn, "other"), 3)

    def test_reapplying_keeps_one_row(self):
        apply_schema(self.conn, "demo", 1, TABLE)
        apply_schema(self.conn, "demo", 1, TABLE)
        count = self.conn.execute("SELECT count(*) FROM schema_versions").fetchone()[0]
        self.assertEqual(count, 1)

    def test_refuses_newer_schema(self):
        apply_schema(self.conn, "demo", 2, TABLE)
        with self.assertRaises(SchemaVersionError):
            apply_schema(self.conn, "demo", 1, TABLE)


if __name__ == "__main__":
    unittest.main()
