"""Blender IDs for the Skin Manager panels."""

from enum import StrEnum

from ....core.ids import ID
from ..constants import NAMESPACE


class PanelID(StrEnum):
    """Panel idnames, e.g. `MAIN` -> `SEDAIA_RIGS_SKINS_PT_skin_manager`.

    Values are explicit so renaming a member never changes the public idname.
    """

    MAIN = ID("skin_manager").panel_for(NAMESPACE)
    HISTORY = ID("skin_history").panel_for(NAMESPACE)  # Saved Skins, a sub-panel of MAIN.


# Sidebar tab the Skin Manager panels appear in. It names no rig, because the
# Skin Manager works on every rig that registers a skin target.
CATEGORY = "Skins"
