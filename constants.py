"""Constants shared by more than one of the extension's packages.

A value belongs here when several packages use it, for example the storage
folders the preferences and the Skin Manager both open. A value only one
package or feature uses stays in that package's own `constants.py`, and every
Blender idname stays with the package that registers it.

These are plain Python, not settings in `blender_manifest.toml`, so loading
the extension never has to read and parse the manifest.

Only the Blender layer imports this module. `core/` cannot: its tests import
`core` as a top-level package, outside this one, so `core/` keeps its own
constants, such as `core.ids.ID_PREFIX`.
"""

from enum import StrEnum
from pathlib import Path

# Full module name Blender registered the extension under, for example
# `bl_ext.user_default.Sakura_Rig_GUI`. `AddonPreferences.bl_idname`,
# `context.preferences.addons`, `extension_path_user`, and
# `addon_utils.module_bl_info` all expect this name. It is this module's own
# package, so it is always the name Blender actually loaded.
ADDON_PACKAGE = __name__.rpartition(".")[0]

# The installed extension's folder, which holds `blender_manifest.toml`, and its
# `lib/` folder of bundled rig files.
EXTENSION_DIR = Path(__file__).resolve().parent
LIB_DIR = EXTENSION_DIR / "lib"


class StorageDir(StrEnum):
    """Subfolders of the extension's user storage directory."""

    ROOT = ""
    RIGS = "rigs"
    PLAYER_DATA = "playerdata"
    PLAYER_DATA_PURGED = "playerdata_purged"  # Backups made by the Skin Manager's purge.


class StorageFile(StrEnum):
    """Files kept directly in the extension's user storage directory."""

    DATABASE = "sakura.sqlite3"


class Sidebar(StrEnum):
    """Where the extension's panels appear: the 3D Viewport's sidebar (N panel).

    Each feature still picks its own tab with `bl_category`.
    """

    SPACE = "VIEW_3D"
    REGION = "UI"
