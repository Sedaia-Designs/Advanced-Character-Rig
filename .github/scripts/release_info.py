"""Collect everything the release workflow needs from the repository.

Used by `.github/workflows/release.yml`. It reads `blender_manifest.toml` and
the changelog it names, checks them, and writes:

- GitHub Actions step outputs: `id`, `name`, `version`, `rig_version`, `tag`,
  `title`, `package`, `prerelease`, `blender_version`, `blender_series`, and
  `blender_sha256`.
- The release notes: the rig's changelog section followed by the extension's.
- The release asset list: every path in `[release]` `artifacts`, one absolute
  path per line.

The rig and the extension keep separate version numbers but ship together, so
one release carries both. The rig version names the release and its tag; the
manifest `version` is the extension's. The release is a pre-release when either
version has a pre-release part.

The manifest's custom `[release]` table configures the release:

- `rig_version` (required): the rig version this release ships, as semver,
  for example `7.5.0-rc.4`.
- `tag_prefix`: the tag is `<tag_prefix><rig_version>`. Default `r`.
- `title`: the release title. `{rig_version}`, `{version}`, and `{name}` are
  replaced, with versions written for people (`7.5.0 RC4`, `4.0.0 Beta 1`).
  Default `{name} {version}`.
- `changelog`: the changelog to take notes from. Default `CHANGELOG.md`. Its
  rig section is headed `## R<rig version>` and its extension section
  `## [<version>]`. For a pre-release, the section of the final version
  (`## R7.5.0`, `## [4.0.0]`) is used when there is none for the pre-release.
- `build_blender_version` and `build_blender_sha256` (required): the Blender
  release that builds the package, and the SHA-256 of its linux-x64 archive.
- `artifacts`: extra files to attach. Default none.

It uses only the standard library, so it runs on any Python 3.11 or newer
without the project environment. It is CI tooling, not extension code, so it
lives outside `core/` and is excluded from the extension build.

Run from the repository root:

    python .github/scripts/release_info.py --notes-out dist/notes.md \
        --assets-out dist/assets.txt --github-output "$GITHUB_OUTPUT"
"""

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

MANIFEST = "blender_manifest.toml"
DEFAULT_CHANGELOG = "CHANGELOG.md"
DEFAULT_TAG_PREFIX = "r"  # r for Revision, as SACR has used since R3
DEFAULT_TITLE = "{name} {version}"
RIG_HEADING = "## R{version}"
EXTENSION_HEADING = "## [{version}]"
TITLE_FIELDS = frozenset({"rig_version", "version", "name"})

# Characters allowed in a tag prefix. Stricter than git's ref rules, so the tag
# is also safe in URLs and shell commands.
TAG_PREFIX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
BLENDER_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

# Semantic version as Blender's manifest requires it: MAJOR.MINOR.PATCH with an
# optional pre-release (`-alpha.1`) and build metadata (`+build.5`).
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?P<pre>[0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$"
)


class ReleaseError(Exception):
    """Raised when the repository is not ready to release."""


@dataclass(frozen=True, slots=True)
class ReleaseInfo:
    """What one release is made of."""

    id: str
    name: str
    version: str
    rig_version: str
    prerelease: bool
    tag_prefix: str
    title_template: str
    blender_version: str
    blender_sha256: str
    assets: tuple[Path, ...]
    notes: str

    @property
    def tag(self) -> str:
        """The git tag for this release, for example `r7.5.0-rc.4`."""
        return f"{self.tag_prefix}{self.rig_version}"

    @property
    def title(self) -> str:
        """The release title, for example `SACR 7.5.0 RC4 + Interface 4.0.0 Beta 1`."""
        return self.title_template.format(
            rig_version=display_version(self.rig_version),
            version=display_version(self.version),
            name=self.name,
        )

    @property
    def blender_series(self) -> str:
        """The Blender download folder version, for example `5.2` for `5.2.2`."""
        return self.blender_version.rsplit(".", 1)[0]

    @property
    def package(self) -> str:
        """The file name `blender --command extension build` gives the package."""
        return f"{self.id}-{self.version}.zip"


def parse_semver(value: str, key: str) -> re.Match[str]:
    """Return the `SEMVER` match for `value`, or raise naming the manifest `key`."""
    match = SEMVER.match(value)
    if match is None:
        raise ReleaseError(f"{MANIFEST}: '{key}' {value!r} is not a semantic version")
    return match


def base_version(version: str) -> str:
    """Return `version` without its pre-release and build parts: `7.5.0-rc.4` -> `7.5.0`."""
    return re.split(r"[-+]", version, maxsplit=1)[0]


def display_version(version: str) -> str:
    """Return a semantic version written for people.

    `7.5.0-rc.4` -> `7.5.0 RC4`, `4.0.0-beta.1` -> `4.0.0 Beta 1`, and
    `4.0.0` -> `4.0.0`. Build metadata is dropped.
    """
    core, _, pre = version.split("+", 1)[0].partition("-")
    if not pre:
        return core
    label, _, number = pre.partition(".")
    if label.lower() == "rc":
        return f"{core} RC{number}"
    words = [label.capitalize(), *number.split(".")] if number else [label.capitalize()]
    return f"{core} {' '.join(words)}"


def check_title(template: str) -> str:
    """Return `template` if it is one line and only uses the supported `{fields}`."""
    if "\n" in template or "\r" in template:
        raise ReleaseError(f"{MANIFEST}: 'release.title' must be a single line")
    fields = set(re.findall(r"{([^{}]*)}", template))
    unknown = fields - TITLE_FIELDS
    if unknown:
        raise ReleaseError(
            f"{MANIFEST}: 'release.title' uses unknown fields {sorted(unknown)}; use {sorted(TITLE_FIELDS)}"
        )
    return template


def read_manifest(root: Path) -> dict:
    """Return the parsed manifest at `root`."""
    path = root / MANIFEST
    try:
        with path.open("rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        raise ReleaseError(f"{MANIFEST} not found in {root}") from None
    except tomllib.TOMLDecodeError as error:
        raise ReleaseError(f"{MANIFEST} is not valid TOML: {error}") from None


def require_string(table: dict, key: str, where: str = "") -> str:
    """Return `table[key]`, which must be a non-empty string.

    `where` prefixes the key in error messages, for example `release.`.
    """
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReleaseError(f"{MANIFEST}: '{where}{key}' must be a non-empty string")
    return value


def optional_string(table: dict, key: str, default: str, where: str = "") -> str:
    """Return `table[key]` if it is set, or `default` if it is not."""
    if key not in table:
        return default
    return require_string(table, key, where)


def release_table(manifest: dict) -> dict:
    """Return the manifest's custom `[release]` table, or an empty one."""
    release = manifest.get("release", {})
    if not isinstance(release, dict):
        raise ReleaseError(f"{MANIFEST}: 'release' must be a table")
    return release


def check_tag_prefix(prefix: str) -> str:
    """Return `prefix` if it is safe to start a git tag with."""
    if not TAG_PREFIX.match(prefix) or ".." in prefix or "//" in prefix:
        raise ReleaseError(f"{MANIFEST}: 'release.tag_prefix' {prefix!r} is not a safe tag prefix")
    return prefix


def parse_blender_version(value: str, key: str) -> tuple[int, int, int]:
    """Return a Blender `X.Y.Z` version string as a tuple of numbers."""
    match = BLENDER_VERSION.match(value)
    if match is None:
        raise ReleaseError(f"{MANIFEST}: '{key}' {value!r} must look like 5.2.2")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def check_build_blender(manifest: dict, release: dict) -> tuple[str, str]:
    """Return the build Blender's version and archive SHA-256.

    The version must be at least `blender_version_min` and, when it is set,
    below `blender_version_max`, which Blender treats as exclusive.
    """
    version = require_string(release, "build_blender_version", "release.")
    build = parse_blender_version(version, "release.build_blender_version")
    minimum = parse_blender_version(require_string(manifest, "blender_version_min"), "blender_version_min")
    if build < minimum:
        raise ReleaseError(
            f"{MANIFEST}: 'release.build_blender_version' {version} is older than blender_version_min"
        )
    if "blender_version_max" in manifest:
        maximum = parse_blender_version(require_string(manifest, "blender_version_max"), "blender_version_max")
        if build >= maximum:
            raise ReleaseError(
                f"{MANIFEST}: 'release.build_blender_version' {version} is not below blender_version_max"
            )

    sha256 = require_string(release, "build_blender_sha256", "release.").lower()
    if not SHA256.match(sha256):
        raise ReleaseError(f"{MANIFEST}: 'release.build_blender_sha256' must be 64 hexadecimal characters")
    return version, sha256


def inside(root: Path, entry: str) -> Path:
    """Return repository path `entry` resolved against `root`, which must contain it.

    A leading `/` is allowed, as in the manifest's `paths_exclude_pattern`.
    """
    root = root.resolve()
    path = (root / entry.lstrip("/")).resolve()
    if not path.is_relative_to(root):
        raise ReleaseError(f"{entry!r} is outside the repository")
    return path


def resolve_assets(root: Path, release: dict) -> tuple[Path, ...]:
    """Return the files listed in the manifest's `[release]` `artifacts`.

    Paths are relative to the repository root. Every path must be a file inside
    the repository, and no two may share a file name, because release assets
    are stored by file name.
    """
    artifacts = release.get("artifacts", [])
    if not isinstance(artifacts, list) or not all(isinstance(item, str) and item.strip() for item in artifacts):
        raise ReleaseError(f"{MANIFEST}: 'release.artifacts' must be a list of paths")

    assets: list[Path] = []
    names: dict[str, str] = {}
    for entry in artifacts:
        try:
            path = inside(root, entry)
        except ReleaseError as error:
            raise ReleaseError(f"Release artifact {error}") from None
        if not path.is_file():
            raise ReleaseError(f"Release artifact {entry!r} does not exist or is not a file")
        if path.name in names:
            raise ReleaseError(f"Release artifacts {names[path.name]!r} and {entry!r} share the file name {path.name!r}")
        names[path.name] = entry
        assets.append(path)
    return tuple(assets)


def changelog_section(text: str, heading: str) -> str | None:
    """Return the body of the section under `heading`, or `None` if there is none.

    `heading` is the whole level-two heading, such as `## [4.0.0]`; text after
    it on the same line, such as a date, is allowed. The section runs until the
    next level-two heading.
    """
    pattern = re.compile(rf"^{re.escape(heading)}(?:\s|$)")
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if pattern.match(line):
            break
    else:
        return None

    body: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body).strip()


def changelog_notes(text: str, template: str, version: str, name: str = DEFAULT_CHANGELOG) -> str:
    """Return the changelog section for `version`, headed by `template`.

    Tries the exact version first, then, for a pre-release, the final version
    it leads to. Raises `ReleaseError` if neither section exists or the one
    found is empty.
    """
    candidates = [template.format(version=version)]
    if base_version(version) != version:
        candidates.append(template.format(version=base_version(version)))

    for heading in candidates:
        notes = changelog_section(text, heading)
        if notes is None:
            continue
        if not notes:
            raise ReleaseError(f"{name} section '{heading}' is empty")
        return notes + "\n"
    raise ReleaseError(f"{name} has no {' or '.join(repr(h) for h in candidates)} section")


def collect(root: Path) -> ReleaseInfo:
    """Read and check everything the release needs from the repository at `root`."""
    manifest = read_manifest(root)
    release = release_table(manifest)
    addon_id = require_string(manifest, "id")
    name = require_string(manifest, "name")
    version = require_string(manifest, "version")
    extension_pre = parse_semver(version, "version").group("pre")
    rig_version = require_string(release, "rig_version", "release.")
    rig_pre = parse_semver(rig_version, "release.rig_version").group("pre")

    title_template = check_title(optional_string(release, "title", DEFAULT_TITLE, "release."))
    tag_prefix = check_tag_prefix(optional_string(release, "tag_prefix", DEFAULT_TAG_PREFIX, "release."))
    blender_version, blender_sha256 = check_build_blender(manifest, release)

    changelog_name = optional_string(release, "changelog", DEFAULT_CHANGELOG, "release.")
    try:
        changelog = inside(root, changelog_name).read_text(encoding="utf-8")
    except ReleaseError as error:
        raise ReleaseError(f"Changelog {error}") from None
    except (FileNotFoundError, IsADirectoryError):
        raise ReleaseError(f"Changelog {changelog_name!r} not found") from None

    rig_notes = changelog_notes(changelog, RIG_HEADING, rig_version, changelog_name)
    extension_notes = changelog_notes(changelog, EXTENSION_HEADING, version, changelog_name)
    notes = (
        f"## Rig {display_version(rig_version)}\n\n{rig_notes}\n"
        f"## {name} {display_version(version)}\n\n{extension_notes}"
    )

    return ReleaseInfo(
        id=addon_id,
        name=name,
        version=version,
        rig_version=rig_version,
        prerelease=extension_pre is not None or rig_pre is not None,
        tag_prefix=tag_prefix,
        title_template=title_template,
        blender_version=blender_version,
        blender_sha256=blender_sha256,
        assets=resolve_assets(root, release),
        notes=notes,
    )


def write_outputs(info: ReleaseInfo, github_output: Path) -> None:
    """Append the step outputs to the file GitHub Actions reads them from."""
    outputs = {
        "id": info.id,
        "name": info.name,
        "version": info.version,
        "rig_version": info.rig_version,
        "tag": info.tag,
        "title": info.title,
        "package": info.package,
        "prerelease": str(info.prerelease).lower(),
        "blender_version": info.blender_version,
        "blender_series": info.blender_series,
        "blender_sha256": info.blender_sha256,
    }
    with github_output.open("a", encoding="utf-8") as file:
        for key, value in outputs.items():
            file.write(f"{key}={value}\n")


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns the process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: current folder)")
    parser.add_argument("--notes-out", type=Path, required=True, help="Where to write the release notes")
    parser.add_argument("--assets-out", type=Path, required=True, help="Where to write the release asset list")
    parser.add_argument("--github-output", type=Path, help="GitHub Actions output file ($GITHUB_OUTPUT)")
    args = parser.parse_args(argv)

    try:
        info = collect(args.root)
    except ReleaseError as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1

    args.notes_out.parent.mkdir(parents=True, exist_ok=True)
    args.notes_out.write_text(info.notes, encoding="utf-8")
    args.assets_out.parent.mkdir(parents=True, exist_ok=True)
    args.assets_out.write_text("".join(f"{path}\n" for path in info.assets), encoding="utf-8")
    if args.github_output:
        write_outputs(info, args.github_output)

    print(f"{info.title} -> tag {info.tag}, package {info.package}")
    print(f"Pre-release: {info.prerelease}")
    print(f"Build Blender: {info.blender_version}")
    for path in info.assets:
        print(f"Release artifact: {path.relative_to(args.root.resolve())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
