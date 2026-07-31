import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


MODULE_PATH = (
    Path(__file__).parents[1]
    / "extension"
    / "lib"
    / "get_files_in_addon_directory.py"
)
extension_package = types.ModuleType("extension")
extension_package.__path__ = [str(MODULE_PATH.parents[1])]
lib_package = types.ModuleType("extension.lib")
lib_package.__path__ = [str(MODULE_PATH.parent)]
preferences_module = types.ModuleType("extension.preferences")
preferences_module.get_preferences = lambda: None

MODULE_SPEC = importlib.util.spec_from_file_location(
    "extension.lib.get_files_in_addon_directory",
    MODULE_PATH,
)
addon_files = importlib.util.module_from_spec(MODULE_SPEC)
with patch.dict(
    sys.modules,
    {
        "extension": extension_package,
        "extension.lib": lib_package,
        "extension.preferences": preferences_module,
    },
):
    MODULE_SPEC.loader.exec_module(addon_files)


class FindFilesInDirectoryWithFilterTests(unittest.TestCase):
    def test_returns_only_files_matching_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "character.blend").touch()
            (root / "character.blend1").touch()
            (root / "notes.txt").touch()

            with patch.object(
                addon_files,
                "get_preferences",
                return_value=SimpleNamespace(addon_data_location=directory),
            ):
                result = addon_files.find_files_in_addon_directory_with_filter(
                    "*.blend*"
                )

        self.assertEqual(
            {Path(file).name for file in result},
            {"character.blend", "character.blend1"},
        )

    def test_searches_nested_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            nested_directory = Path(directory) / "rigs"
            nested_directory.mkdir()
            expected_file = nested_directory / "character.blend"
            expected_file.touch()

            with patch.object(
                addon_files,
                "get_preferences",
                return_value=SimpleNamespace(addon_data_location=directory),
            ):
                result = addon_files.find_files_in_addon_directory_with_filter(
                    "*.blend*"
                )

        self.assertEqual(result, [str(expected_file)])

    def test_supports_multiple_whitelist_patterns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blend_file = root / "character.blend"
            json_file = root / "manifest.json"
            ignored_file = root / "preview.png"
            for file in (blend_file, json_file, ignored_file):
                file.touch()

            with patch.object(
                addon_files,
                "get_preferences",
                return_value=SimpleNamespace(addon_data_location=directory),
            ):
                result = addon_files.find_files_in_addon_directory_with_filter(
                    ["*.blend", "*.json"]
                )

        self.assertEqual(set(result), {str(blend_file), str(json_file)})


if __name__ == "__main__":
    unittest.main()
