import hashlib
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).parents[1]
EXTENSION_ROOT = PROJECT_ROOT / "src"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


extension_package = types.ModuleType("src")
extension_package.__path__ = [str(EXTENSION_ROOT)]
lib_package = types.ModuleType("src.sru_lib")
lib_package.__path__ = [str(EXTENSION_ROOT / "sru_lib")]
rig_manager_package = types.ModuleType("src.rig_manager")
rig_manager_package.__path__ = [str(EXTENSION_ROOT / "rig_manager")]
rig_manager_lib_package = types.ModuleType("src.rig_manager.lib")
rig_manager_lib_package.__path__ = [str(EXTENSION_ROOT / "rig_manager" / "lib")]

with patch.dict(
    sys.modules,
    {
        "src": extension_package,
        "src.sru_lib": lib_package,
        "src.rig_manager": rig_manager_package,
        "src.rig_manager.lib": rig_manager_lib_package,
    },
):
    exceptions = _load_module(
        "src.sru_lib.exceptions",
        EXTENSION_ROOT / "sru_lib" / "exceptions.py",
    )
    hash_module = _load_module(
        "src.sru_lib.hash",
        EXTENSION_ROOT / "sru_lib" / "hash.py",
    )

    http_module = types.ModuleType("src.sru_lib.http")
    lib_package.exceptions = exceptions
    lib_package.hash = hash_module
    lib_package.http = http_module
    sys.modules["src.sru_lib.http"] = http_module

    manifest = _load_module(
        "src.rig_manager.lib.manifest",
        EXTENSION_ROOT / "rig_manager" / "lib" / "manifest.py",
    )


class ManifestDownloadTests(unittest.TestCase):
    source_url = "https://example.test/sacr-index.json"
    checksum_url = "https://example.test/sacr-index.json.sha256"
    timeout = 7

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.destination = Path(self.temporary_directory.name).resolve()
        self.manifest_path = self.destination / "sacr-index.json"
        self.checksum_path = self.destination / "sacr-index.json.sha256"
        self.manifest_tmp = self.destination / "sacr-index.json.tmp"
        self.checksum_tmp = self.destination / "sacr-index.json.sha256.tmp"

    def tearDown(self):
        self.temporary_directory.cleanup()

    @staticmethod
    def checksum(contents: bytes) -> str:
        return hashlib.sha256(contents).hexdigest()

    def write_local_pair(
        self,
        manifest_contents: bytes,
        checksum: str | None = None,
    ):
        self.manifest_path.write_bytes(manifest_contents)
        self.checksum_path.write_text(
            checksum or self.checksum(manifest_contents),
            encoding="utf-8",
        )

    def call_download(self):
        return manifest.download(
            source_url=self.source_url,
            checksum_url=self.checksum_url,
            destination=self.destination,
            timeout=self.timeout,
        )

    def test_requires_destination(self):
        with self.assertRaisesRegex(
            ValueError,
            "Destination path must be provided",
        ):
            manifest.download(destination=None)

    def test_missing_local_artifact_delegates_complete_download(self):
        self.manifest_path.write_bytes(b"orphaned manifest")
        expected_result = {
            "file_path": self.manifest_path,
            "checksum_path": self.checksum_path,
            "sha256_string": self.checksum(b"downloaded manifest"),
        }

        with patch.object(
            manifest.http,
            "download_with_checksum",
            return_value=expected_result,
            create=True,
        ) as download_with_checksum:
            result = self.call_download()

        self.assertEqual(result, self.manifest_path)
        download_with_checksum.assert_called_once_with(
            self.source_url,
            self.checksum_url,
            self.manifest_path,
            self.timeout,
        )

    def test_current_local_pair_skips_payload_download(self):
        current_contents = b'{"version": 1}'
        current_checksum = self.checksum(current_contents)
        self.write_local_pair(current_contents)

        def download_checksum(url, destination, timeout):
            self.assertEqual(url, self.checksum_url)
            self.assertEqual(timeout, self.timeout)
            Path(destination).write_text(current_checksum, encoding="utf-8")
            return Path(destination)

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_checksum,
            create=True,
        ) as http_download:
            result = self.call_download()

        self.assertEqual(result, self.manifest_path)
        self.assertEqual(http_download.call_count, 1)
        self.assertEqual(self.manifest_path.read_bytes(), current_contents)
        self.assertFalse(self.manifest_tmp.exists())
        self.assertFalse(self.checksum_tmp.exists())

    def test_repairs_stale_checksum_without_downloading_payload(self):
        current_contents = b'{"version": 2}'
        remote_checksum = self.checksum(current_contents)
        self.write_local_pair(current_contents, checksum="0" * 64)

        def download_checksum(url, destination, timeout):
            self.assertEqual(url, self.checksum_url)
            Path(destination).write_text(remote_checksum, encoding="utf-8")
            return Path(destination)

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_checksum,
            create=True,
        ) as http_download:
            result = self.call_download()

        self.assertEqual(result, self.manifest_path)
        self.assertEqual(http_download.call_count, 1)
        self.assertEqual(
            self.checksum_path.read_text(encoding="utf-8"),
            remote_checksum,
        )

    def test_repairs_malformed_local_checksum_without_payload_download(self):
        current_contents = b'{"version": 3}'
        remote_checksum = self.checksum(current_contents)
        self.write_local_pair(current_contents, checksum="not-a-checksum")

        def download_checksum(url, destination, timeout):
            self.assertEqual(url, self.checksum_url)
            Path(destination).write_text(remote_checksum, encoding="utf-8")
            return Path(destination)

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_checksum,
            create=True,
        ) as http_download:
            result = self.call_download()

        self.assertEqual(result, self.manifest_path)
        self.assertEqual(http_download.call_count, 1)
        self.assertEqual(
            self.checksum_path.read_text(encoding="utf-8"),
            remote_checksum,
        )

    def test_updates_stale_manifest_and_checksum(self):
        old_contents = b'{"version": 1}'
        new_contents = b'{"version": 2}'
        new_checksum = self.checksum(new_contents)
        self.write_local_pair(old_contents)

        def download_file(url, destination, timeout):
            destination = Path(destination)
            if url == self.checksum_url:
                destination.write_text(new_checksum, encoding="utf-8")
            elif url == self.source_url:
                destination.write_bytes(new_contents)
            else:
                self.fail(f"Unexpected URL: {url}")
            return destination

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_file,
            create=True,
        ) as http_download:
            result = self.call_download()

        self.assertEqual(result, self.manifest_path)
        self.assertEqual(http_download.call_count, 2)
        self.assertEqual(self.manifest_path.read_bytes(), new_contents)
        self.assertEqual(
            self.checksum_path.read_text(encoding="utf-8"),
            new_checksum,
        )
        self.assertFalse(self.manifest_tmp.exists())
        self.assertFalse(self.checksum_tmp.exists())

    def test_rejects_malformed_remote_checksum_and_cleans_temporary_file(self):
        original_contents = b'{"version": 1}'
        self.write_local_pair(original_contents)

        def download_checksum(url, destination, timeout):
            Path(destination).write_text("invalid", encoding="utf-8")
            return Path(destination)

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_checksum,
            create=True,
        ):
            with self.assertRaises(exceptions.ChecksumValidationError):
                self.call_download()

        self.assertEqual(self.manifest_path.read_bytes(), original_contents)
        self.assertFalse(self.manifest_tmp.exists())
        self.assertFalse(self.checksum_tmp.exists())

    def test_rejects_payload_with_wrong_checksum_and_preserves_local_pair(self):
        original_contents = b'{"version": 1}'
        original_checksum = self.checksum(original_contents)
        expected_contents = b'{"version": 2}'
        expected_checksum = self.checksum(expected_contents)
        corrupt_download = b"incomplete response"
        self.write_local_pair(original_contents)

        def download_file(url, destination, timeout):
            destination = Path(destination)
            if url == self.checksum_url:
                destination.write_text(expected_checksum, encoding="utf-8")
            elif url == self.source_url:
                destination.write_bytes(corrupt_download)
            else:
                self.fail(f"Unexpected URL: {url}")
            return destination

        with patch.object(
            manifest.http,
            "download",
            side_effect=download_file,
            create=True,
        ):
            with self.assertRaises(exceptions.ChecksumValidationError):
                self.call_download()

        self.assertEqual(self.manifest_path.read_bytes(), original_contents)
        self.assertEqual(
            self.checksum_path.read_text(encoding="utf-8"),
            original_checksum,
        )
        self.assertFalse(self.manifest_tmp.exists())
        self.assertFalse(self.checksum_tmp.exists())


if __name__ == "__main__":
    unittest.main()
