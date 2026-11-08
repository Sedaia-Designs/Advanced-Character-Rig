import bpy.types as T

from ....core.skin_targets import registry as skin_targets
from .constants import OperatorID


class SkinRouter(T.Operator):
    bl_idname = OperatorID.ROUTER
    bl_label = "Skin Manager"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """Only run on a rig whose feature registered a Skin Manager target."""
        return skin_targets.for_rig(context.active_object) is not None

    def execute(self, context):
        rig = context.active_object
        target = skin_targets.for_rig(rig)
        if target is None:
            self.report({"ERROR"}, "The active object is not a rig the Skin Manager supports")
            return {"CANCELLED"}

        settings = rig.pose.bones.get(target.username.bone)
        if settings is None:
            self.report({"ERROR"}, f"{target.label} rig is missing its '{target.username.bone}' bone")
            return {"CANCELLED"}

        username = settings.get(target.username.key, "")

        return {'FINISHED'}


classes = (SkinRouter,)
