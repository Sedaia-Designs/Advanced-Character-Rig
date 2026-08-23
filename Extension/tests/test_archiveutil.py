import importlib.util
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

EXTENSION_ROOT = Path(__file__).parents[1] / "src"
FILE_PATH = EXTENSION_ROOT / "sru_lib" / "file.py"
EXCEPTIONS_PATH = EXTENSION_ROOT / "sru_lib" / "exceptions.py"

extension_package = types.ModuleType("src")
extension_package.__path__ = [str(EXTENSION_ROOT)]
lib_package = types.ModuleType("src.sru_lib")
lib_package.__path__ = [str(EXTENSION_ROOT / "sru_lib")]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


with patch.dict(
    sys.modules,
    {
        "src": extension_package,
        "src.sru_lib": lib_package,
    },
):
    exceptions = _load_module("src.sru_lib.exceptions", EXCEPTIONS_PATH)
    file_util = _load_module("src.sru_lib.file", FILE_PATH)


class ZipExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.archive_path = self.root / "rig.zip"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_archive(self, members: dict[str, str]) -> None:
        with zipfile.ZipFile(self.archive_path, "w") as archive:
            for filename, contents in members.items():
                archive.writestr(filename, contents)

    def test_extracts_matching_files_within_maximum_depth(self):
        self.write_archive(
            {
                "file1.txt": "root text",
                "file2.py": "root python",
                "Subdir/sub_file1.txt": "nested text",
                "Subdir/sub_file4.py": "nested python",
                "Subdir/deeper/ignored.py": "too deep",
            }
        )
        destination = self.root / "extracted"

        file_util.Zip(self.archive_path).extract(
            destination,
            only_glob=["*.py"],
            max_depth=1,
        )

        self.assertEqual((destination / "file2.py").read_text(), "root python")
        self.assertEqual(
            (destination / "Subdir" / "sub_file4.py").read_text(),
            "nested python",
        )
        self.assertFalse((destination / "file1.txt").exists())
        self.assertFalse((destination / "Subdir" / "sub_file1.txt").exists())
        self.assertFalse((destination / "Subdir" / "deeper" / "ignored.py").exists())

    def test_empty_glob_extracts_all_files(self):
        self.write_archive({"file1.txt": "root", "Subdir/file2.py": "nested"})
        destination = self.root / "extracted"

        file_util.Zip(self.archive_path).extract(destination, only_glob=[])

        self.assertTrue((destination / "file1.txt").is_file())
        self.assertTrue((destination / "Subdir" / "file2.py").is_file())

    def test_rejects_member_that_escapes_destination(self):
        self.write_archive({"../outside.txt": "unsafe"})

        with self.assertRaises(exceptions.UnsafeArchiveMemberError):
            file_util.Zip(self.archive_path).extract(
                self.root / "extracted",
                only_glob=[],
            )

    def test_rejects_windows_style_member_paths(self):
        self.write_archive({"Subdir\\outside.txt": "unsafe"})

        with self.assertRaises(exceptions.UnsafeArchiveMemberError):
            file_util.Zip(self.archive_path).extract(
                self.root / "extracted",
                only_glob=[],
            )

    def test_wraps_invalid_zip_files(self):
        self.archive_path.write_text("not a zip")

        with self.assertRaises(exceptions.ArchiveExtractionError):
            file_util.Zip(self.archive_path).extract(
                self.root / "extracted",
                only_glob=[],
            )


if __name__ == "__main__":
    unittest.main()
