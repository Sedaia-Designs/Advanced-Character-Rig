"""Read the extension's `blender_manifest.toml` without Blender.

Pattern: Adapter. `read_manifest` converts the raw TOML table into a typed
`Manifest`, so no other code reads manifest keys by string.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

MANIFEST_FILENAME = "blender_manifest.toml"


class ManifestError(ValueError):
    """Raised when a manifest is missing required fields or does not match its package."""


@dataclass(frozen=True, slots=True)
class Manifest:
    """The identity fields of a Blender extension manifest."""

    id: str
    name: str
    version: str


def read_manifest(path: Path) -> Manifest:
    """Parse the manifest at `path` and return its identity fields.

    Raises `FileNotFoundError` if the file is missing, `tomllib.TOMLDecodeError`
    if it is not valid TOML, and `ManifestError` if a required field is missing
    or is not a non-empty string.
    """
    with path.open("rb") as file:
        data = tomllib.load(file)

    fields = {}
    for key in ("id", "name", "version"):
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise ManifestError(f"{path.name}: '{key}' must be a non-empty string")
        fields[key] = value

    return Manifest(**fields)


def addon_package(package: str, addon_id: str) -> str:
    """Return the extension's root package name from any package inside it.

    Blender loads an extension as `bl_ext.<repository>.<id>`, and that full
    dotted name is what `AddonPreferences.bl_idname` and
    `bpy.utils.extension_path_user` expect. For example,
    `addon_package("bl_ext.user_default.My_Addon.preferences", "My_Addon")`
    returns `"bl_ext.user_default.My_Addon"`.

    Raises `ManifestError` if no segment of `package` equals `addon_id`, which
    means the extension was installed under a folder name that differs from
    its manifest ID.
    """
    parts = package.split(".")
    try:
        index = len(parts) - 1 - parts[::-1].index(addon_id)
    except ValueError:
        raise ManifestError(
            f"Package '{package}' is not inside an extension with ID '{addon_id}'. "
            "The extension's folder name must match the manifest ID."
        ) from None
    return ".".join(parts[: index + 1])
