"""Extension identity, read from `blender_manifest.toml` when the package loads."""

from enum import StrEnum
from pathlib import Path

from ..core.manifest import MANIFEST_FILENAME, addon_package, read_manifest

MANIFEST = read_manifest(Path(__file__).resolve().parents[1] / MANIFEST_FILENAME)

# Full module name Blender registered the extension under, e.g.
# `bl_ext.user_default.Sakura_Rig_GUI`. `AddonPreferences.bl_idname`,
# `context.preferences.addons`, and `extension_path_user` all expect this name.
ADDON_PACKAGE = addon_package(__package__, MANIFEST.id)


class StorageDir(StrEnum):
    """Subfolders of the extension's user storage directory."""

    ROOT = ""
    RIGS = "rigs"
    PLAYER_DATA = "playerdata"
    PLAYER_DATA_PURGED = "playerdata_purged"  # Backups made by the Skin Manager's purge.


class StorageFile(StrEnum):
    """Files kept directly in the extension's user storage directory."""

    DATABASE = "sakura.sqlite3"
