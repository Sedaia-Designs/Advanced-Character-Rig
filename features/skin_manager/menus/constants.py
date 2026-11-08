"""Blender IDs for the Skin Manager menus."""

from enum import StrEnum

from ....core.ids import ID
from ..constants import NAMESPACE


class MenuID(StrEnum):
    """Menu idnames, e.g. `EXISTING` -> `SEDAIA_RIGS_SKINS_MT_existing`.

    Values are explicit so renaming a member never changes the public idname.
    """

    # Shown when the player is already stored: load, check for a new skin, or purge.
    EXISTING = ID("existing").menu_for(NAMESPACE)
