"""Sync the player named on the rig from Mojang, then apply their current skin."""

import asyncio

import bpy
import bpy.types as T

from .base import OFFLINE_MESSAGE, REPORTED_ERRORS, SkinOperator, build_manager, call_operator
from .constants import OperatorID


class SkinAdd(SkinOperator, T.Operator):
    """Check Mojang for the player's current skin, download it if it is new, and apply it"""

    bl_idname = OperatorID.ADD
    bl_label = "Check for New Skin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not bpy.app.online_access:
            self.report({"ERROR"}, OFFLINE_MESSAGE)
            return {"CANCELLED"}
        found = self.rig_target(context)
        if found is None:
            return {"CANCELLED"}
        username = self.username(*found)
        if username is None:
            return {"CANCELLED"}

        # Blocks Blender while it runs. Every request has a 10 s timeout, and a
        # sync is two small JSON lookups and at most two small PNGs.
        try:
            result = asyncio.run(build_manager().sync(username))
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        if not result.downloaded:
            self.report({"INFO"}, f"{result.player.name}'s skin has not changed; using the stored copy")
        if not call_operator(self, OperatorID.LOAD, index=result.skin.index):
            return {"CANCELLED"}
        return {"FINISHED"}


classes = (SkinAdd,)
