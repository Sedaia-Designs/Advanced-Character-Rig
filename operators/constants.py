"""Blender IDs for the extension's shared operators."""

from enum import StrEnum

from ..core.ids import ID

NAMESPACE = "UTILS"


class OperatorID(StrEnum):
    """Operator idnames, e.g. `IMAGE_PACK` -> `sedaia_rigs_utils_ot.image_pack`.

    Values are explicit so renaming a member never changes the public idname.
    """

    # File Operations
    FILE_OPEN = ID("file_open").operator_for(NAMESPACE)
    FILE_DELETE = ID("file_delete").operator_for(NAMESPACE)

    # Image Operations
    IMAGE_PACK = ID("image_pack").operator_for(NAMESPACE)
    IMAGE_RELOAD = ID("image_reload").operator_for(NAMESPACE)

    # Rig Operations
    RIG_RENAME = ID("rig_rename").operator_for(NAMESPACE)
