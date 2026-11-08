"""Decide what to do with the username on the rig: load, ask, download, or refuse."""

import bpy
import bpy.props as P
import bpy.types as T

from ....core.skin_manager import Route, route
from ....preferences.access import get_prefs
from ..menus.constants import MenuID
from .base import OFFLINE_MESSAGE, REPORTED_ERRORS, SkinOperator, build_manager, call_operator
from .constants import OperatorID


class SkinRouter(SkinOperator, T.Operator):
    """Apply the skin of the Minecraft Java Edition player named on the rig"""

    bl_idname = OperatorID.ROUTER
    bl_label = "Change Skin"
    bl_options = {"REGISTER", "UNDO"}

    blocked_while_syncing = True

    use_modal: P.BoolProperty(
        name="Run in Background",
        description="Download without blocking Blender. Set when run from the UI",
        default=False,
        options={"HIDDEN", "SKIP_SAVE"},
    )

    def invoke(self, context, event):
        self.use_modal = True
        return self.execute(context)

    def execute(self, context):
        found = self.rig_target(context)
        if found is None:
            return {"CANCELLED"}
        username = self.username(*found)
        if username is None:
            return {"CANCELLED"}

        try:
            has_local = build_manager().find_local(username) is not None
        except REPORTED_ERRORS as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        prefs = get_prefs(context)
        prompt = prefs.prompt_to_refresh_player_data if prefs is not None else True

        add_context = "INVOKE_DEFAULT" if self.use_modal else "EXEC_DEFAULT"
        match route(has_local, bpy.app.online_access, prompt):
            case Route.LOAD:
                result = call_operator(self, OperatorID.LOAD, index=-1)
            case Route.DOWNLOAD:
                result = call_operator(self, OperatorID.ADD, add_context)
            case Route.PROMPT:
                # The menu arrives in Phase 4. Until it is registered, check
                # for a new skin, which downloads only if the skin changed.
                if hasattr(bpy.types, MenuID.EXISTING):
                    bpy.ops.wm.call_menu(name=MenuID.EXISTING)
                    return {"FINISHED"}
                result = call_operator(self, OperatorID.ADD, add_context)
            case Route.OFFLINE_ERROR:
                self.report({"ERROR"}, f"{username} is not stored yet. {OFFLINE_MESSAGE}")
                return {"CANCELLED"}

        return {"FINISHED"} if result else {"CANCELLED"}


classes = (SkinRouter,)
