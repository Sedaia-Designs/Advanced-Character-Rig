import bpy.types as T
import bpy.props as P

from .constants import OperatorID


class RIGS_set_name(T.Operator):
    bl_idname = OperatorID.RIG_RENAME
    bl_label = "Set Rig Name"
    bl_options = {"REGISTER", "UNDO"}

    name: P.StringProperty()
    update_collection: P.BoolProperty()

    def execute(self, context):
        obj = context.active_object
        obj.name = self.name
        obj.data.name = self.name

        if self.update_collection is True:
            try:
                obj.users_collection[0].name = self.name
            except (AttributeError, KeyError):
                context.asset.name = self.name

        return {"FINISHED"}

classes = (
    RIGS_set_name,
)
