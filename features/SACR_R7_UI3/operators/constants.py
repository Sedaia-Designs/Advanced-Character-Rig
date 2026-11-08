"""Blender IDs for the SACR R7.5 operators."""

from enum import StrEnum

from ....core.ids import ID
from ..ui import RIG_ID_GROUP as NAMESPACE


class OperatorID(StrEnum):
    """Operator idnames, e.g. `TOGGLE_COLLECTION` -> `sedaia_rigs_sacr7_ui3.toggle_collection`."""

    TOGGLE_COLLECTION = ID("toggle_collection").operator_for(NAMESPACE)
    ADD_RIG = ID("add_rig").operator_for(NAMESPACE)  # Append a new R7.5 rig at the 3D Cursor.
