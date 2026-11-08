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
        # A menu opened with `wm.call_menu` runs its items' `execute` by
        # default, which would skip Purge's confirmation and block Blender
        # during Check for New Skin. Invoking runs the confirmation and the
        # background download.
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(OperatorID.LOAD, text="Load Saved Skin", icon="FILE_REFRESH").index = -1
        layout.operator(OperatorID.ADD, text="Check for New Skin", icon="URL")
        layout.separator()
        layout.operator(OperatorID.PURGE, text="Back Up and Purge", icon="DUPLICATE").backup = True
        layout.operator(OperatorID.PURGE, text="Purge", icon="ERROR").backup = False


classes = (MT_Existing,)
