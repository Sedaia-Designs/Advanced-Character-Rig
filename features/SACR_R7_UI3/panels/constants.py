"""Blender IDs for the SACR R7.5 panels."""

from enum import StrEnum

from ....core.ids import ID
from ..ui import RIG_ID_GROUP as NAMESPACE


class PanelID(StrEnum):
    """Panel idnames, e.g. `MAIN` -> `SEDAIA_RIGS_SACR7_UI3_PT_main`."""

    MAIN = ID("main").panel_for(NAMESPACE)
    FACE = ID("face").panel_for(NAMESPACE)
    COLLECTIONS = ID("collections").panel_for(NAMESPACE)
    ADD_RIG = ID("add_rig").panel_for(NAMESPACE)  # Shown with or without a rig selected.
