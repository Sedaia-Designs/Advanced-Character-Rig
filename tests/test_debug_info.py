"""Blender-free tests for `core.debug_info` and `core.databases.schema.schema_versions`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import json
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases.schema import apply_schema, schema_versions  # noqa: E402
from core.debug_info import UNKNOWN, format_report, manifest_version, text, version_text  # noqa: E402


class ManifestVersionTests(unittest.TestCase):
    def test_keeps_prerelease(self):
        self.assertEqual(manifest_version('id = "X"\nversion = "4.0.0-beta.1"\n'), "4.0.0-beta.1")

    def test_missing_or_invalid(self):
        for source in ('id = "X"\n', 'version = 4\n', 'version = ""\n', "version = "):
            with self.subTest(source=source):
                self.assertIsNone(manifest_version(source))

    def test_reads_this_repositorys_manifest(self):
        manifest = Path(__file__).resolve().parents[1] / "blender_manifest.toml"
        self.assertTrue(manifest_version(manifest.read_text(encoding="utf-8")))


class TextTests(unittest.TestCase):
    def test_version_text(self):
        self.assertEqual(version_text((5, 2, 2)), "5.2.2")
        self.assertEqual(version_text("7.5.0"), "7.5.0")
        for value in (None, (), "", 3):
            with self.subTest(value=value):
                self.assertEqual(version_text(value), UNKNOWN)

    def test_text(self):
        self.assertEqual(text(b"d13f752e3b9c"), "d13f752e3b9c")
        self.assertEqual(text(b""), UNKNOWN)
        self.assertEqual(text(None), UNKNOWN)
        self.assertEqual(text(7), "7")


class FormatReportTests(unittest.TestCase):
    def test_json_code_block_keeps_order(self):
        report = format_report({"extension": {"version": "4.0.0"}, "rig": {"rig version": "7.5.0"}})
        self.assertTrue(report.startswith("```json\n") and report.endswith("\n```"))
        body = json.loads(report.removeprefix("```json\n").removesuffix("\n```"))
        self.assertEqual(list(body), ["extension", "rig"])
        self.assertEqual(body["rig"]["rig version"], "7.5.0")

    def test_unserializable_values_use_str(self):
        report = format_report({"system": {"path": Path("x")}})
        self.assertIn('"path": "x"', report)


class SchemaVersionsTests(unittest.TestCase):
    def test_empty_database(self):
        with sqlite3.connect(":memory:") as conn:
            self.assertEqual(schema_versions(conn), {})

    def test_lists_every_schema(self):
        with sqlite3.connect(":memory:") as conn:
            apply_schema(conn, "skin_manager", 1, ())
            apply_schema(conn, "rigs", 2, ())
            self.assertEqual(schema_versions(conn), {"rigs": 2, "skin_manager": 1})


if __name__ == "__main__":
    unittest.main()
