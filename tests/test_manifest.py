"""Blender-free tests for the manifest reader.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.manifest import MANIFEST_FILENAME, ManifestError, addon_package, read_manifest  # noqa: E402


class ReadManifestTests(unittest.TestCase):
    def write(self, text: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / MANIFEST_FILENAME
        path.write_text(text, encoding="utf-8")
        return path

    def test_reads_repository_manifest(self):
        manifest = read_manifest(ROOT / MANIFEST_FILENAME)
        self.assertTrue(manifest.id)

    def test_reads_identity_fields(self):
        manifest = read_manifest(self.write('id = "My_Addon"\nname = "My Addon"\nversion = "1.2.3"\n'))
        self.assertEqual((manifest.id, manifest.name, manifest.version), ("My_Addon", "My Addon", "1.2.3"))

    def test_missing_id(self):
        with self.assertRaises(ManifestError):
            read_manifest(self.write('name = "My Addon"\nversion = "1.2.3"\n'))

    def test_non_string_version(self):
        with self.assertRaises(ManifestError):
            read_manifest(self.write('id = "My_Addon"\nname = "My Addon"\nversion = 1\n'))

    def test_invalid_toml(self):
        with self.assertRaises(tomllib.TOMLDecodeError):
            read_manifest(self.write("id = "))

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_manifest(ROOT / "missing.toml")


class AddonPackageTests(unittest.TestCase):
    def test_from_subpackage(self):
        self.assertEqual(
            addon_package("bl_ext.user_default.My_Addon.preferences", "My_Addon"),
            "bl_ext.user_default.My_Addon",
        )

    def test_from_root_package(self):
        self.assertEqual(addon_package("bl_ext.user_default.My_Addon", "My_Addon"), "bl_ext.user_default.My_Addon")

    def test_nested_segment_with_same_name(self):
        self.assertEqual(addon_package("bl_ext.repo.My_Addon.features.My_Addon", "My_Addon"), "bl_ext.repo.My_Addon.features.My_Addon")

    def test_folder_name_differs_from_id(self):
        with self.assertRaises(ManifestError):
            addon_package("bl_ext.pycharm_blender.Sakura_Character_Rig.preferences", "Sakura_Rig_GUI")


if __name__ == "__main__":
    unittest.main()
