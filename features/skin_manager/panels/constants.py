"""Blender IDs for the Skin Manager panels."""

from enum import StrEnum

from ....core.ids import ID
from ..constants import NAMESPACE


class PanelID(StrEnum):
    """Panel idnames, e.g. `MAIN` -> `SEDAIA_RIGS_SKINS_PT_skin_manager`.

    Values are explicit so renaming a member never changes the public idname.
    """

    MAIN = ID("skin_manager").panel_for(NAMESPACE)
