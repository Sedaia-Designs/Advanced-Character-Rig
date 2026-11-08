"""Blender IDs for the Skin Manager operators."""

from enum import StrEnum

from ....core.ids import ID
from ..constants import NAMESPACE


class OperatorID(StrEnum):
    """Operator idnames, e.g. `ROUTER` -> `sedaia_rigs_skins_ot.skin_router`.

    Values are explicit so renaming a member never changes the public idname.
    """

    ROUTER = ID("skin_router").operator_for(NAMESPACE)
    ADD = ID("skin_add").operator_for(NAMESPACE)
