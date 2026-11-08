"""The menu the router opens when the player on the rig is already stored.

Replaces the legacy "regen" and "purge" menus. The purge confirmation is the
`PURGE` operator's own dialog, so no second menu is needed.
"""

import bpy.types as T

from ..operators.constants import OperatorID
from .constants import MenuID


class MT_Existing(T.Menu):
    bl_idname = MenuID.EXISTING
    bl_label = "Player Already Saved"

    def draw(self, context):
        layout = self.layout
        # Menu items run their operator's invoke, so Check for New Skin and
        # Purge download in the background and Purge asks for confirmation.
        layout.operator(OperatorID.LOAD, text="Load Saved Skin", icon="FILE_REFRESH").index = -1
        layout.operator(OperatorID.ADD, text="Check for New Skin", icon="URL")
        layout.separator()
        layout.operator(OperatorID.PURGE, text="Back Up and Purge", icon="DUPLICATE").backup = True
        layout.operator(OperatorID.PURGE, text="Purge", icon="ERROR").backup = False


classes = (MT_Existing,)
