"""Blender-free tests for `core.skin_manager`, with in-memory SQLite and a fake Mojang client.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import asyncio
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases.skins import SkinDatabase, SkinModel  # noqa: E402
from core.mojang import MojangURL, PlayerNotFoundError, Profile, TextureRef  # noqa: E402
from core.network import NetworkError  # noqa: E402
from core.background import BackgroundTask  # noqa: E402
from core.skin_manager import (  # noqa: E402
    DefaultSkinError,
    MissingTextureError,
    Route,
    SkinManager,
    SkinManagerError,
    SkinNotStoredError,
    SyncCancelledError,
    SyncProgress,
    SyncStage,
    route,
    stage_progress,
    stage_text,
)

UUID = "069a79f444e94726a5befca90e38aaf5"
OTHER = "853c80ef3c3749fdaa49938b674adae6"
SKIN_A = "aa" * 32
SKIN_B = "bb" * 32
CAPE_A = "cc" * 32


def texture(texture_hash: str, model: SkinModel | None = None) -> TextureRef:
    return TextureRef(MojangURL.TEXTURES + texture_hash, texture_hash, model)


class FakeHTTP:
    """Write a small body for each download, or raise for URLs listed in `fail`."""

    def __init__(self):
        self.downloads: list[str] = []
        self.fail: set[str] = set()

    async def download(self, url: str, dest: Path) -> None:
        self.downloads.append(url)
        if url in self.fail:
            raise NetworkError("textures.minecraft.net answered with HTTP 500")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"png")


class FakeMojang:
    """Serve one profile per name. Change `profiles` between syncs to simulate skin changes."""

    def __init__(self):
        self.http = FakeHTTP()
        self.profiles: dict[str, Profile] = {}

    async def lookup(self, name: str) -> tuple[str, str]:
        for profile in self.profiles.values():
            if profile.name.lower() == name.strip().lower():
                return profile.uuid, profile.name
        raise PlayerNotFoundError(f"No Minecraft player is named {name!r}")

    async def profile(self, uuid: str) -> Profile:
        return self.profiles[uuid]


class ManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.player_data = root / "playerdata"
        self.purged = root / "playerdata_purged"

        self.conn = sqlite3.connect(":memory:")
        self.addCleanup(self.conn.close)
        with self.conn:
            SkinDatabase(self.conn).create_schema()

        @contextmanager
        def session():
            with self.conn:
                yield self.conn

        self.mojang = FakeMojang()
        self.manager = SkinManager(session, self.mojang, self.player_data, self.purged)  # pyright: ignore[reportArgumentType]

    def set_profile(self, skin: TextureRef | None, cape: TextureRef | None = None,
                    name: str = "Notch", uuid: str = UUID) -> None:
        self.mojang.profiles[uuid] = Profile(uuid, name, skin, cape)

    def sync(self, name: str = "Notch"):
        return asyncio.run(self.manager.sync(name))

    @property
    def db(self) -> SkinDatabase:
        return SkinDatabase(self.conn)


class RouteTests(unittest.TestCase):
    def test_every_combination(self):
        cases = {
            (True, True, True): Route.PROMPT,
            (True, True, False): Route.LOAD,
            (True, False, True): Route.LOAD,
            (True, False, False): Route.LOAD,
            (False, True, True): Route.DOWNLOAD,
            (False, True, False): Route.DOWNLOAD,
            (False, False, True): Route.OFFLINE_ERROR,
            (False, False, False): Route.OFFLINE_ERROR,
        }
        for args, expected in cases.items():
            with self.subTest(args=args):
                self.assertEqual(route(*args), expected)


class SyncTests(ManagerTestCase):
    def test_new_player_downloads_skin_and_cape(self):
        self.set_profile(texture(SKIN_A, SkinModel.SLIM), texture(CAPE_A))
        result = self.sync("notch")

        self.assertTrue(result.downloaded)
        self.assertEqual((result.player.uuid, result.player.name), (UUID, "Notch"))
        self.assertEqual(result.skin.path, f"{UUID}/skin_{SKIN_A}.png")
        self.assertEqual(result.skin.model, SkinModel.SLIM)
        self.assertEqual(result.cape.path, f"{UUID}/cape_{CAPE_A}.png")
        self.assertTrue((self.player_data / UUID / f"skin_{SKIN_A}.png").is_file())
        self.assertTrue((self.player_data / UUID / f"cape_{CAPE_A}.png").is_file())

    def test_same_skin_again_is_deduplicated_by_hash(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        first = self.sync()
        second = self.sync()

        self.assertFalse(second.downloaded)
        self.assertEqual(second.skin, first.skin)
        self.assertEqual(len(self.db.skins(UUID)), 1)
        self.assertEqual(len(self.mojang.http.downloads), 1)

    def test_changed_skin_adds_a_new_entry(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()
        self.set_profile(texture(SKIN_B, SkinModel.SLIM))
        result = self.sync()

        self.assertTrue(result.downloaded)
        self.assertEqual(result.skin.index, 1)
        self.assertEqual([s.hash for s in self.db.skins(UUID)], [SKIN_A, SKIN_B])

    def test_same_texture_with_new_model_reuses_the_file(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()
        self.set_profile(texture(SKIN_A, SkinModel.SLIM))
        result = self.sync()

        self.assertFalse(result.downloaded)
        self.assertEqual(result.skin.model, SkinModel.SLIM)
        self.assertEqual(len(self.db.skins(UUID)), 2)

    def test_renamed_player_keeps_their_history(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC), name="OldName")
        self.sync("OldName")
        self.set_profile(texture(SKIN_B, SkinModel.CLASSIC), name="NewName")
        result = self.sync("NewName")

        self.assertEqual(result.player.name, "NewName")
        self.assertEqual(len(self.db.skins(UUID)), 2)
        self.assertIsNone(self.manager.find_local("OldName"))
        self.assertEqual(self.manager.find_local("newname").uuid, UUID)

    def test_failed_download_leaves_no_rows_or_new_files(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC), texture(CAPE_A))
        self.mojang.http.fail.add(MojangURL.TEXTURES + CAPE_A)
        with self.assertRaises(NetworkError):
            self.sync()

        self.assertIsNone(self.db.player(UUID))
        self.assertFalse((self.player_data / UUID / f"skin_{SKIN_A}.png").exists())

    def test_missing_file_is_downloaded_again(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()
        (self.player_data / UUID / f"skin_{SKIN_A}.png").unlink()
        result = self.sync()

        self.assertTrue(result.downloaded)
        self.assertEqual(len(self.db.skins(UUID)), 1)
        self.assertTrue((self.player_data / UUID / f"skin_{SKIN_A}.png").is_file())

    def test_default_skin_raises(self):
        self.set_profile(None)
        with self.assertRaises(DefaultSkinError):
            self.sync()
        self.assertIsNone(self.db.player(UUID))

    def test_unknown_player_raises(self):
        with self.assertRaises(PlayerNotFoundError):
            self.sync("nobody")

    def test_subscribers_see_each_stage(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC), texture(CAPE_A))
        stages = []
        unsubscribe = self.manager.subscribe(lambda stage, _name: stages.append(stage))
        self.sync()
        self.assertEqual(stages, list(SyncStage))

        unsubscribe()
        self.sync()
        self.assertEqual(len(stages), len(SyncStage))


class CancelTests(ManagerTestCase):
    def cancel_at(self, stage: SyncStage):
        """Sync with a cancel check that turns true once `stage` has been published."""
        seen: list[SyncStage] = []
        self.manager.subscribe(lambda s, _name: seen.append(s))
        return asyncio.run(self.manager.sync("Notch", should_cancel=lambda: stage in seen))

    def test_cancelling_at_each_stage_writes_nothing(self):
        stages = (SyncStage.LOOKUP, SyncStage.PROFILE, SyncStage.DOWNLOAD_SKIN, SyncStage.DOWNLOAD_CAPE)
        for stage in stages:
            with self.subTest(stage=stage):
                self.set_profile(texture(SKIN_A, SkinModel.CLASSIC), texture(CAPE_A))
                with self.assertRaises(SyncCancelledError) as caught:
                    self.cancel_at(stage)
                self.assertIsInstance(caught.exception, SkinManagerError)
                self.assertIsNone(self.db.player(UUID))
                self.assertEqual(list(self.player_data.glob("*/*.png")), [])
                self.manager._listeners.clear()

    def test_cancel_before_start_makes_no_request(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        with self.assertRaises(SyncCancelledError):
            asyncio.run(self.manager.sync("Notch", should_cancel=lambda: True))
        self.assertEqual(self.mojang.http.downloads, [])

    def test_sync_in_a_background_task(self):
        self.conn.close()  # The worker thread needs its own connections.
        database = Path(self.temp.name) / "skins.sqlite3"

        from core.sql import SQLite

        manager = SkinManager(SQLite(database).session, self.mojang, self.player_data, self.purged)  # pyright: ignore[reportArgumentType]
        self.set_profile(texture(SKIN_A, SkinModel.SLIM))
        task = BackgroundTask()
        manager.subscribe(lambda stage, name: task.publish((stage, name)))
        task.start(lambda: manager.sync("Notch", should_cancel=task.cancelled))
        self.assertTrue(task.wait(5))

        progress = SyncProgress()
        progress.start("Notch", task)
        progress.update(task.drain())
        self.assertEqual(task.result().skin.model, SkinModel.SLIM)
        self.assertEqual(progress.stage, SyncStage.DONE)
        self.assertEqual(progress.fraction, 1.0)


class ProgressTests(unittest.TestCase):
    def test_stage_progress_increases_to_one(self):
        values = [stage_progress(stage) for stage in SyncStage]
        self.assertEqual(values, sorted(values))
        self.assertGreater(values[0], 0)
        self.assertEqual(values[-1], 1.0)

    def test_every_stage_has_text(self):
        for stage in SyncStage:
            self.assertIn("Notch", stage_text(stage, "Notch"))

    def test_sync_progress_lifecycle(self):
        progress = SyncProgress()
        task = BackgroundTask()
        self.assertFalse(progress.running)
        progress.start("notch", task)
        self.assertTrue(progress.running)
        self.assertEqual(progress.fraction, 0.0)
        self.assertIn("notch", progress.text)
        with self.assertRaises(RuntimeError):
            progress.start("jeb", BackgroundTask())

        progress.update([(SyncStage.LOOKUP, "notch"), (SyncStage.PROFILE, "Notch")])
        self.assertEqual((progress.stage, progress.name), (SyncStage.PROFILE, "Notch"))
        self.assertEqual(progress.text, stage_text(SyncStage.PROFILE, "Notch"))

        progress.cancel()
        self.assertTrue(task.cancelled())
        self.assertIn("Cancelling", progress.text)
        progress.reset()
        self.assertFalse(progress.running)
        progress.cancel()  # No task: nothing to cancel, and no error.


class SelectionTests(ManagerTestCase):
    def test_newest_and_indexed_selection(self):
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()
        self.set_profile(texture(SKIN_B, SkinModel.SLIM))
        self.sync()

        newest = self.manager.selection(UUID)
        self.assertEqual(newest.path, self.player_data / UUID / f"skin_{SKIN_B}.png")
        self.assertEqual(newest.model, SkinModel.SLIM)
        self.assertEqual(self.manager.selection(UUID, 0).model, SkinModel.CLASSIC)

    def test_missing_skin_and_missing_file(self):
        with self.assertRaises(SkinNotStoredError):
            self.manager.selection(UUID)

        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()
        with self.assertRaises(SkinNotStoredError):
            self.manager.selection(UUID, 5)
        (self.player_data / UUID / f"skin_{SKIN_A}.png").unlink()
        with self.assertRaises(MissingTextureError):
            self.manager.selection(UUID)


class PurgeTests(ManagerTestCase):
    def setUp(self):
        super().setUp()
        self.set_profile(texture(SKIN_A, SkinModel.CLASSIC))
        self.sync()

    def test_purge_without_backup_deletes_rows_and_folder(self):
        self.assertTrue(self.manager.purge(UUID, backup=False))
        self.assertIsNone(self.db.player(UUID))
        self.assertFalse((self.player_data / UUID).exists())
        self.assertFalse(self.purged.exists())

    def test_purge_with_backup_moves_the_folder_to_a_numbered_path(self):
        self.manager.purge(UUID, backup=True)
        self.assertTrue((self.purged / f"{UUID}_1" / f"skin_{SKIN_A}.png").is_file())

        self.sync()
        self.manager.purge(UUID, backup=True)
        self.assertTrue((self.purged / f"{UUID}_2").is_dir())
        self.assertIsNone(self.db.player(UUID))

    def test_purge_leaves_other_players_alone(self):
        self.set_profile(texture(SKIN_B, SkinModel.CLASSIC), name="Jeb", uuid=OTHER)
        self.sync("Jeb")
        self.manager.purge(UUID, backup=False)
        self.assertTrue((self.player_data / OTHER).is_dir())
        self.assertIsNotNone(self.db.player(OTHER))

    def test_purge_of_unknown_player_returns_false(self):
        self.assertFalse(self.manager.purge(OTHER, backup=False))


class LegacyImportTests(ManagerTestCase):
    def write_legacy(self, folder: Path, name: str, data) -> Path:
        path = folder / name / f"{name}_Data.json"
        path.parent.mkdir(parents=True)
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return path

    def legacy(self, name: str, uuid: str) -> dict:
        skin = self.player_data / name / f"{name}_Skin.png"
        return {
            "UUID": uuid,
            "NAME": name,
            "SKINS": [{"index": 0, "path": str(skin), "hash": SKIN_A, "model": "1"}],
            "CAPES": [{"index": 0, "path": "", "hash": "", "exists": False}],
        }

    def test_good_and_bad_files(self):
        legacy_dir = self.player_data
        self.write_legacy(legacy_dir, "Notch", self.legacy("Notch", UUID))
        bad_json = self.write_legacy(legacy_dir, "Broken", "{not json")
        bad_shape = self.write_legacy(legacy_dir, "Shapeless", {"UUID": OTHER, "NAME": "Shapeless"})

        report = self.manager.import_legacy_dir(legacy_dir)

        self.assertEqual([p.uuid for p in report.imported], [UUID])
        self.assertEqual({path for path, _ in report.failed}, {bad_json, bad_shape})
        self.assertEqual(self.db.latest_skin(UUID).model, SkinModel.SLIM)
        self.assertIsNone(self.db.player(OTHER))

    def test_purge_also_moves_a_legacy_username_folder(self):
        data = self.legacy("Notch", UUID)
        self.write_legacy(self.player_data, "Notch", data)
        Path(data["SKINS"][0]["path"]).write_bytes(b"png")
        self.manager.import_legacy_dir(self.player_data)

        self.manager.purge(UUID, backup=True)
        self.assertFalse((self.player_data / "Notch").exists())
        self.assertTrue((self.purged / "Notch_1" / "Notch_Data.json").is_file())


if __name__ == "__main__":
    unittest.main()
