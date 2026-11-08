import bpy.types as T

from .constants import OperatorID


class SkinAdd(T.Operator):
    bl_idname = OperatorID.ADD
    bl_label = "Add Skin"

    def execute(self, context):
        return {'FINISHED'}


classes = (SkinAdd,)
