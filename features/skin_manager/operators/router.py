import bpy.types as T

from ..constants import ConfigBone
from .constants import OperatorID


class SkinRouter(T.Operator):
    bl_idname = OperatorID.ROUTER
    bl_label = "Skin Manager"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        rig = context.active_object
        rig_bones: T.PoseBone = rig.pose.bones

        options = rig_bones[ConfigBone.ARGUMENTS]
        materials = rig_bones[ConfigBone.MATERIAL_LIB]

        return {'FINISHED'}


classes = (SkinRouter,)
