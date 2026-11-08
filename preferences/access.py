"""Read the extension's preferences and storage paths from anywhere in the add-on.

Operators, panels, and `AddonPreferences.draw()` all need these, so they live
in one shared module instead of being repeated in each.

This module must stay a leaf: it may import only `bpy`, `core/`, and
`.constants`. `preferences/addon_preferences.py` imports `operators.constants`,
which loads the whole `operators` package. Any operator can import from here
safely, because nothing here imports back into `operators/`.
"""

from typing import TYPE_CHECKING, Optional

import bpy
from bpy.utils import extension_path_user

from .constants import ADDON_PACKAGE, StorageDir

if TYPE_CHECKING:
    from .addon_preferences import PREFS_user_preferences


def get_prefs(context: Optional[bpy.types.Context] = None) -> Optional["PREFS_user_preferences"]:
    """Return this extension's preferences, or `None` if it is not enabled."""
    context = context or bpy.context
    addon = context.preferences.addons.get(ADDON_PACKAGE)
    return addon.preferences if addon else None


def storage_dir(folder: StorageDir = StorageDir.ROOT) -> str:
    """Return a folder in the extension's user storage, creating it if needed."""
    return extension_path_user(ADDON_PACKAGE, create=True, path=folder)
