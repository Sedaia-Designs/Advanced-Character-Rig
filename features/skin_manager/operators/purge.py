"""Delete everything stored for the player named on the rig, then download them again."""

import bpy
import bpy.props as P
import bpy.types as T

from .base import OFFLINE_MESSAGE, REPORTED_ERRORS, SkinOperator, build_manager, call_operator
from .constants import OperatorID


class SkinPurge(SkinOperator, T.Operator):
    """Delete the player's stored skins and capes, then download their current skin again"""

    bl_idname = OperatorID.PURGE
    bl_label = "Purge Player Data"
    bl_options = {"REGISTER", "UNDO"}

    backup: P.BoolProperty(
        name="Back Up",
        description="Move the player's files to the purged player data folder instead of deleting them",
        default=False,
    )

    def invoke(self, context, event):
        message = "Their files will be moved to a backup folder." if self.backup else "Their files will be deleted."
        return context.window_manager.invoke_confirm(
            self, event, title="Purge Player Data?", message=message, confirm_text="Purge", icon="WARNING"
        )

    def execute(self, context):
        # Purging is followed by a fresh download, so refuse before deleting
        # anything if that download cannot happen.
        if not bpy.app.online_access:
            self.report({"ERROR"}, OFFLINE_MESSAGE)
            return {"CANCELLED"}
        found = self.rig_target(context)
        if found is None:
            return {"CANCELLED"}
        username = self.username(*found)
        if username is None:
            return {"CANCELLED"}

        manager = build_manager()
        try:
            player = manager.find_local(username)
            if player is not None:
                manager.purge(player.uuid, backup=self.backup)
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        if player is not None:
            action = "Backed up" if self.backup else "Deleted"
            self.report({"INFO"}, f"{action} the stored data for {player.name}")
        if not call_operator(self, OperatorID.ADD):
            return {"CANCELLED"}
        return {"FINISHED"}


classes = (SkinPurge,)
