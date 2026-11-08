"""Blender IDs for the Skin Manager operators."""

from enum import StrEnum

from ....core.ids import ID
from ..constants import NAMESPACE


class OperatorID(StrEnum):
    """Operator idnames, e.g. `ROUTER` -> `sedaia_rigs_skins.skin_router`.

    Values are explicit so renaming a member never changes the public idname.
    """

    ROUTER = ID("skin_router").operator_for(NAMESPACE)  # Decide what to do with the username.
    ADD = ID("skin_add").operator_for(NAMESPACE)  # Sync from Mojang, then apply.
    LOAD = ID("skin_load").operator_for(NAMESPACE)  # Apply a stored skin, offline.
    PURGE = ID("skin_purge").operator_for(NAMESPACE)  # Delete a player's data, then re-sync.
    IMPORT_LEGACY = ID("skin_import_legacy").operator_for(NAMESPACE)  # Import legacy JSON files.
