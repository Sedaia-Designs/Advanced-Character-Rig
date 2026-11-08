"""Tests for the release workflow helper, `.github/scripts/release_info.py`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "release_info.py"
_spec = importlib.util.spec_from_file_location("release_info", SCRIPT)
assert _spec is not None and _spec.loader is not None
release_info = importlib.util.module_from_spec(_spec)
sys.modules["release_info"] = release_info  # dataclasses look the module up by name
_spec.loader.exec_module(release_info)

CHANGELOG = """# Changelog

## SACR rig

## R7.5.0

- Rig change.

## R7.4.1

- Old rig change.

## Blender extension

## [1.2.0] - 2026-11-08

### Added

- New thing.

## [1.1.0] - 2026-01-01

- Old thing.
"""

SHA = "a" * 64
BUILD = f'build_blender_version = "5.2.2"\nbuild_blender_sha256 = "{SHA}"\n'
RIG = 'rig_version = "7.5.0"\n'


def manifest(version="1.2.0", release=None, extra=""):
    """Return manifest text; `release` replaces the whole `[release]` table body."""
    if release is None:
        release = RIG + BUILD + 'artifacts = ["/lib/rig.blend"]\n'
    return (
        f'id = "My_Addon"\nname = "My Addon"\nversion = "{version}"\n'
        f'blender_version_min = "5.2.0"\n{extra}\n[release]\n{release}'
    )


class RepoTestCase(unittest.TestCase):
    """Builds a throwaway repository with a manifest, changelog, and one artifact."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "lib").mkdir()
        (self.root / "lib" / "rig.blend").write_bytes(b"BLENDER")
        (self.root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
        self.write_manifest(manifest())

    def tearDown(self):
        self._tmp.cleanup()

    def write_manifest(self, text):
        (self.root / "blender_manifest.toml").write_text(text, encoding="utf-8")


class CollectTests(RepoTestCase):
    def test_tag_follows_rig_version_and_package_follows_extension(self):
        info = release_info.collect(self.root)
        self.assertEqual(info.tag, "v7.5.0")
        self.assertEqual(info.package, "My_Addon-1.2.0.zip")
        self.assertFalse(info.prerelease)

    def test_resolves_artifacts_from_repository_root(self):
        info = release_info.collect(self.root)
        self.assertEqual(info.assets, ((self.root / "lib" / "rig.blend").resolve(),))

    def test_rig_prerelease_marks_prerelease(self):
        self.write_manifest(manifest(release='rig_version = "7.5.0-rc.4"\n' + BUILD))
        info = release_info.collect(self.root)
        self.assertTrue(info.prerelease)
        self.assertEqual(info.tag, "v7.5.0-rc.4")

    def test_extension_prerelease_marks_prerelease(self):
        self.write_manifest(manifest(version="1.2.0-beta.1", release=RIG + BUILD))
        self.assertTrue(release_info.collect(self.root).prerelease)

    def test_requires_rig_version(self):
        self.write_manifest(manifest(release=BUILD))
        with self.assertRaisesRegex(release_info.ReleaseError, "rig_version"):
            release_info.collect(self.root)

    def test_rejects_non_semantic_versions(self):
        for text in (manifest(version="1.2"), manifest(release='rig_version = "R7.5"\n' + BUILD)):
            with self.subTest(text=text):
                self.write_manifest(text)
                with self.assertRaisesRegex(release_info.ReleaseError, "semantic version"):
                    release_info.collect(self.root)

    def test_defaults_without_optional_settings(self):
        self.write_manifest(manifest(release=RIG + BUILD))
        info = release_info.collect(self.root)
        self.assertEqual(info.assets, ())
        self.assertEqual(info.title, "My Addon 1.2.0")

    def test_custom_tag_prefix(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'tag_prefix = "sacr-"\n'))
        self.assertEqual(release_info.collect(self.root).tag, "sacr-7.5.0")

    def test_rejects_unsafe_tag_prefix(self):
        for prefix in ("has space/", "../x", "-x", "a//b"):
            with self.subTest(prefix=prefix):
                self.write_manifest(manifest(release=RIG + BUILD + f'tag_prefix = "{prefix}"\n'))
                with self.assertRaisesRegex(release_info.ReleaseError, "safe tag prefix"):
                    release_info.collect(self.root)

    def test_title_template(self):
        self.write_manifest(manifest(
            version="1.2.0-beta.1",
            release='rig_version = "7.5.0-rc.4"\n' + BUILD + 'title = "SACR {rig_version} + Interface {version}"\n',
        ))
        self.assertEqual(release_info.collect(self.root).title, "SACR 7.5.0 RC4 + Interface 1.2.0 Beta 1")

    def test_rejects_unknown_title_field(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'title = "{rig} {version}"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "unknown fields"):
            release_info.collect(self.root)

    def test_rejects_multiline_title(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'title = "a\\nb"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "single line"):
            release_info.collect(self.root)

    def test_notes_combine_rig_and_extension_sections(self):
        notes = release_info.collect(self.root).notes
        self.assertEqual(
            notes,
            "## Rig 7.5.0\n\n- Rig change.\n\n## My Addon 1.2.0\n\n### Added\n\n- New thing.\n",
        )

    def test_prerelease_notes_fall_back_to_final_sections(self):
        self.write_manifest(manifest(version="1.2.0-beta.1", release='rig_version = "7.5.0-rc.4"\n' + BUILD))
        notes = release_info.collect(self.root).notes
        self.assertIn("## Rig 7.5.0 RC4\n\n- Rig change.", notes)
        self.assertIn("## My Addon 1.2.0 Beta 1\n\n### Added", notes)

    def test_rejects_missing_rig_section(self):
        self.write_manifest(manifest(release='rig_version = "7.6.0"\n' + BUILD))
        with self.assertRaisesRegex(release_info.ReleaseError, "## R7.6.0"):
            release_info.collect(self.root)

    def test_custom_changelog(self):
        (self.root / "docs").mkdir()
        (self.root / "docs" / "NOTES.md").write_text("## R7.5.0\n\n- Rig.\n\n## [1.2.0]\n\n- Custom.\n", encoding="utf-8")
        self.write_manifest(manifest(release=RIG + BUILD + 'changelog = "docs/NOTES.md"\n'))
        self.assertIn("- Custom.", release_info.collect(self.root).notes)

    def test_rejects_missing_changelog(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'changelog = "MISSING.md"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "not found"):
            release_info.collect(self.root)

    def test_rejects_changelog_outside_repository(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'changelog = "../CHANGELOG.md"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "outside the repository"):
            release_info.collect(self.root)

    def test_build_blender_outputs(self):
        info = release_info.collect(self.root)
        self.assertEqual((info.blender_version, info.blender_series, info.blender_sha256), ("5.2.2", "5.2", SHA))

    def test_requires_build_blender(self):
        self.write_manifest(manifest(release=RIG))
        with self.assertRaisesRegex(release_info.ReleaseError, "build_blender_version"):
            release_info.collect(self.root)

    def test_rejects_build_blender_below_minimum(self):
        self.write_manifest(manifest(release=RIG + f'build_blender_version = "5.1.1"\nbuild_blender_sha256 = "{SHA}"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "older than blender_version_min"):
            release_info.collect(self.root)

    def test_rejects_build_blender_at_maximum(self):
        self.write_manifest(manifest(extra='blender_version_max = "5.2.2"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "not below blender_version_max"):
            release_info.collect(self.root)

    def test_rejects_malformed_build_blender_version(self):
        self.write_manifest(manifest(release=RIG + f'build_blender_version = "5.2"\nbuild_blender_sha256 = "{SHA}"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "must look like"):
            release_info.collect(self.root)

    def test_rejects_malformed_sha256(self):
        self.write_manifest(manifest(release=RIG + 'build_blender_version = "5.2.2"\nbuild_blender_sha256 = "abc"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "64 hexadecimal"):
            release_info.collect(self.root)

    def test_rejects_missing_artifact(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'artifacts = ["/lib/missing.blend"]\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "does not exist"):
            release_info.collect(self.root)

    def test_rejects_directory_artifact(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'artifacts = ["/lib"]\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "not a file"):
            release_info.collect(self.root)

    def test_rejects_artifact_outside_repository(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'artifacts = ["../outside.blend"]\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "outside the repository"):
            release_info.collect(self.root)

    def test_rejects_artifacts_with_the_same_file_name(self):
        (self.root / "other").mkdir()
        (self.root / "other" / "rig.blend").write_bytes(b"BLENDER")
        self.write_manifest(manifest(release=RIG + BUILD + 'artifacts = ["/lib/rig.blend", "other/rig.blend"]\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "share the file name"):
            release_info.collect(self.root)

    def test_rejects_non_list_artifacts(self):
        self.write_manifest(manifest(release=RIG + BUILD + 'artifacts = "/lib/rig.blend"\n'))
        with self.assertRaisesRegex(release_info.ReleaseError, "list of paths"):
            release_info.collect(self.root)


class DisplayVersionTests(unittest.TestCase):
    def test_formats(self):
        cases = {
            "7.5.0": "7.5.0",
            "7.5.0-rc.4": "7.5.0 RC4",
            "4.0.0-beta.1": "4.0.0 Beta 1",
            "4.0.0-alpha": "4.0.0 Alpha",
            "4.0.0-beta.1+build.7": "4.0.0 Beta 1",
        }
        for version, expected in cases.items():
            with self.subTest(version=version):
                self.assertEqual(release_info.display_version(version), expected)


class ChangelogNotesTests(unittest.TestCase):
    def test_returns_only_the_version_section(self):
        notes = release_info.changelog_notes(CHANGELOG, release_info.EXTENSION_HEADING, "1.2.0")
        self.assertEqual(notes, "### Added\n\n- New thing.\n")

    def test_rig_heading(self):
        notes = release_info.changelog_notes(CHANGELOG, release_info.RIG_HEADING, "7.4.1")
        self.assertEqual(notes, "- Old rig change.\n")

    def test_exact_prerelease_section_wins(self):
        text = "## [2.0.0-beta.1]\n\n- Beta.\n\n## [2.0.0]\n\n- Final.\n"
        self.assertEqual(release_info.changelog_notes(text, release_info.EXTENSION_HEADING, "2.0.0-beta.1"), "- Beta.\n")

    def test_does_not_match_a_longer_version(self):
        with self.assertRaisesRegex(release_info.ReleaseError, "no '## \\[1.2\\]' section"):
            release_info.changelog_notes(CHANGELOG, release_info.EXTENSION_HEADING, "1.2")

    def test_rejects_empty_section(self):
        with self.assertRaisesRegex(release_info.ReleaseError, "is empty"):
            release_info.changelog_notes("## [3.0.0]\n\n## [2.0.0]\n- Old.\n", release_info.EXTENSION_HEADING, "3.0.0")


class MainTests(RepoTestCase):
    def test_writes_notes_assets_and_outputs(self):
        out = self.root / "out"
        code = release_info.main([
            "--root", str(self.root),
            "--notes-out", str(out / "notes.md"),
            "--assets-out", str(out / "assets.txt"),
            "--github-output", str(self.root / "github_output"),
        ])
        self.assertEqual(code, 0)
        self.assertIn("- New thing.", (out / "notes.md").read_text(encoding="utf-8"))
        self.assertEqual((out / "assets.txt").read_text(encoding="utf-8").splitlines(), [str((self.root / "lib" / "rig.blend").resolve())])
        outputs = dict(line.split("=", 1) for line in (self.root / "github_output").read_text(encoding="utf-8").splitlines())
        self.assertEqual(outputs["tag"], "v7.5.0")
        self.assertEqual(outputs["rig_version"], "7.5.0")
        self.assertEqual(outputs["title"], "My Addon 1.2.0")
        self.assertEqual(outputs["package"], "My_Addon-1.2.0.zip")
        self.assertEqual(outputs["prerelease"], "false")
        self.assertEqual(outputs["blender_series"], "5.2")
        self.assertEqual(outputs["blender_sha256"], SHA)

    def test_returns_error_code_when_not_ready(self):
        (self.root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        out = self.root / "out"
        code = release_info.main(["--root", str(self.root), "--notes-out", str(out / "n"), "--assets-out", str(out / "a")])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
