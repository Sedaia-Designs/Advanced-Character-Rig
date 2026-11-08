"""Blender-free tests for `core.databases.skins`, run against in-memory SQLite.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases import skins  # noqa: E402
from core.databases.skins import (  # noqa: E402
    LegacyFormatError,
    SkinDatabase,
    SkinModel,
    normalize_uuid,
    parse_legacy,
)
from core.databases.schema import SchemaVersionError  # noqa: E402
from core.sql import SQLite  # noqa: E402

UUID = "069a79f444e94726a5befca90e38aaf5"
DASHED = "069A79F4-44E9-4726-A5BE-FCA90E38AAF5"
OTHER = "853c80ef3c3749fdaa49938b674adae6"


def legacy_file(**overrides):
    """Return a legacy `<name>_Data.json` payload as the old skin manager wrote it."""
    data = {
        "UUID": UUID,
        "NAME": "Notch",
        "SKINS": [
            {"index": 0, "path": "/old/Notch/Notch_Skin.png", "hash": "aaa", "model": "0"},
            {"index": 1, "path": "/old/Notch/Notch_Skin_1.png", "hash": "bbb", "model": "1"},
        ],
        "CAPES": [
            {"index": 0, "path": "/old/Notch/Notch_Cape.png", "hash": "ccc", "exists": True},
            {"index": 1, "path": "", "hash": "", "exists": False},
        ],
    }
    data.update(overrides)
    return data


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        self.db = SkinDatabase(self.conn)
        self.db.create_schema()


class SchemaTests(DatabaseTestCase):
    def test_records_version(self):
        self.assertEqual(self.db.schema_version(), skins.SCHEMA_VERSION)

    def test_create_is_idempotent(self):
        self.db.create_schema()
        rows = self.conn.execute("SELECT count(*) FROM schema_versions").fetchone()
        self.assertEqual(rows[0], 1)

    def test_no_version_before_create(self):
        with sqlite3.connect(":memory:") as conn:
            self.assertIsNone(SkinDatabase(conn).schema_version())

    def test_refuses_newer_schema(self):
        self.conn.execute("UPDATE schema_versions SET version = version + 1")
        with self.assertRaises(SchemaVersionError):
            self.db.create_schema()

    def test_create_keeps_callers_transaction_open(self):
        with tempfile.TemporaryDirectory() as folder:
            factory = SQLite(Path(folder) / "test.sqlite3")
            with self.assertRaises(RuntimeError), factory.session() as conn:
                db = SkinDatabase(conn)
                db.create_schema()
                db.upsert_player(UUID, "Notch")
                raise RuntimeError("roll back")
            with factory.session() as conn:
                self.assertIsNone(SkinDatabase(conn).schema_version())


class PlayerTests(DatabaseTestCase):
    def test_upsert_normalizes_uuid(self):
        player = self.db.upsert_player(DASHED, "Notch")
        self.assertEqual(player.uuid, UUID)
        self.assertEqual(self.db.player(UUID), player)

    def test_upsert_renames(self):
        self.db.upsert_player(UUID, "Notch")
        self.db.upsert_player(UUID, "NotNotch")
        self.assertEqual(self.db.player(UUID).name, "NotNotch")
        self.assertEqual(len(self.db.players()), 1)

    def test_find_ignores_case(self):
        self.db.upsert_player(UUID, "Notch")
        self.assertEqual(self.db.find_player("nOTCH").uuid, UUID)
        self.assertIsNone(self.db.find_player("jeb_"))

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            self.db.upsert_player("not-a-uuid", "Notch")
        with self.assertRaises(ValueError):
            self.db.upsert_player(UUID, "")

    def test_delete_cascades(self):
        self.db.upsert_player(UUID, "Notch")
        self.db.add_skin(UUID, "aaa", "Notch/skin.png", SkinModel.CLASSIC)
        self.db.add_cape(UUID, "ccc", "Notch/cape.png")
        self.assertTrue(self.db.delete_player(UUID))
        self.assertFalse(self.db.delete_player(UUID))
        self.assertEqual(self.db.skins(UUID), [])
        self.assertEqual(self.db.capes(UUID), [])


class TextureTests(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.db.upsert_player(UUID, "Notch")

    def test_indexes_count_up_per_player(self):
        self.db.upsert_player(OTHER, "jeb_")
        first = self.db.add_skin(UUID, "aaa", "a.png", SkinModel.CLASSIC)
        second = self.db.add_skin(UUID, "bbb", "b.png", SkinModel.SLIM)
        other = self.db.add_skin(OTHER, "zzz", "z.png", SkinModel.CLASSIC)
        self.assertEqual((first.index, second.index, other.index), (0, 1, 0))
        self.assertIs(second.model, SkinModel.SLIM)

    def test_latest_and_index_lookup(self):
        self.assertIsNone(self.db.latest_skin(UUID))
        self.db.add_skin(UUID, "aaa", "a.png", SkinModel.CLASSIC)
        self.db.add_skin(UUID, "bbb", "b.png", SkinModel.SLIM)
        self.assertEqual(self.db.latest_skin(UUID).hash, "bbb")
        self.assertEqual(self.db.skin(UUID, -1).hash, "bbb")
        self.assertEqual(self.db.skin(UUID, 0).hash, "aaa")
        self.assertIsNone(self.db.skin(UUID, 5))

    def test_find_by_hash(self):
        self.db.add_skin(UUID, "aaa", "a.png", SkinModel.CLASSIC)
        self.db.add_cape(UUID, "ccc", "c.png")
        self.assertEqual(self.db.find_skin(UUID, "aaa").path, "a.png")
        self.assertIsNone(self.db.find_skin(UUID, "ccc"))
        self.assertEqual(self.db.find_cape(UUID, "ccc").index, 0)

    def test_requires_existing_player(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_skin(OTHER, "aaa", "a.png", SkinModel.CLASSIC)

    def test_rejects_taken_index(self):
        self.db.add_cape(UUID, "ccc", "c.png", index=3)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.add_cape(UUID, "ddd", "d.png", index=3)
        self.assertEqual(self.db.add_cape(UUID, "ddd", "d.png").index, 4)

    def test_rejects_unknown_model(self):
        with self.assertRaises(ValueError):
            self.db.add_skin(UUID, "aaa", "a.png", "wide")  # type: ignore[arg-type]


class LegacyImportTests(DatabaseTestCase):
    def test_imports_legacy_file(self):
        player = self.db.import_legacy(legacy_file())
        self.assertEqual((player.uuid, player.name), (UUID, "Notch"))
        skins = self.db.skins(UUID)
        self.assertEqual([s.model for s in skins], [SkinModel.CLASSIC, SkinModel.SLIM])
        self.assertEqual(skins[1].path, "/old/Notch/Notch_Skin_1.png")
        capes = self.db.capes(UUID)
        self.assertEqual([(c.index, c.hash) for c in capes], [(0, "ccc")])

    def test_reimport_replaces_textures(self):
        self.db.import_legacy(legacy_file())
        self.db.import_legacy(legacy_file(SKINS=[], CAPES=[]))
        self.assertEqual(self.db.skins(UUID), [])
        self.assertEqual(self.db.capes(UUID), [])

    def test_bad_file_writes_nothing(self):
        bad = legacy_file(SKINS=[{"index": 0, "path": "x", "hash": "y", "model": "2"}])
        with self.assertRaises(LegacyFormatError):
            self.db.import_legacy(bad)
        self.assertEqual(self.db.players(), [])


class ParseLegacyTests(unittest.TestCase):
    def test_missing_capes_list_is_allowed(self):
        data = legacy_file()
        del data["CAPES"]
        self.assertEqual(parse_legacy(data).capes, ())

    def test_rejects_malformed_files(self):
        cases = {
            "uuid": legacy_file(UUID="nope"),
            "name": legacy_file(NAME=""),
            "skins type": legacy_file(SKINS="none"),
            "skin entry": legacy_file(SKINS=["bad"]),
            "bool index": legacy_file(SKINS=[{"index": True, "path": "", "hash": "", "model": "0"}]),
            "duplicate": legacy_file(SKINS=[
                {"index": 0, "path": "a", "hash": "a", "model": "0"},
                {"index": 0, "path": "b", "hash": "b", "model": "0"},
            ]),
            "capes type": legacy_file(CAPES={}),
        }
        for label, data in cases.items():
            with self.subTest(label), self.assertRaises(LegacyFormatError):
                parse_legacy(data)


class NormalizeUuidTests(unittest.TestCase):
    def test_accepts_dashed_and_upper_case(self):
        self.assertEqual(normalize_uuid(DASHED), UUID)

    def test_rejects_wrong_length_or_characters(self):
        for value in ("", UUID[:-1], "g" * 32):
            with self.subTest(value), self.assertRaises(ValueError):
                normalize_uuid(value)


if __name__ == "__main__":
    unittest.main()
