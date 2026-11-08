"""Blender IDs for the SACR R7.5 operators."""

from enum import StrEnum

from ....core.ids import ID
from ..ui import RIG_ID_GROUP as NAMESPACE


class OperatorID(StrEnum):
    """Operator idnames, e.g. `TOGGLE_COLLECTION` -> `sedaia_rigs_sacr7_ui3_ot.toggle_collection`."""

    TOGGLE_COLLECTION = ID("toggle_collection").operator_for(NAMESPACE)
