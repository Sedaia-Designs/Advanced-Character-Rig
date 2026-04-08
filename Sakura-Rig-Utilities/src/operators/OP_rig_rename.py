import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from ..preferences import Prefixer, get_preferences

class OP_rig_rename(T.Operator):
    """Rename the active armature and its data, optionally updating its collection name."""
    bl_label = "Set Rig Name"
    bl_idname = Prefixer("rig_rename").operator
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(
        name="New Name",
        description="The new name for the rig",
        default=""
    )

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        if not self.name:
            self.report({'WARNING'}, "No name provided.")
            return {'CANCELLED'}

        obj = context.active_object
        obj.name = self.name
        if obj.data:
            obj.data.name = self.name

        if get_preferences().sync_collection_name_with_rig:
            try:
                obj = context.active_object
                if obj.users_collection:
                    obj.users_collection[0].name = self.name
            except (AttributeError, KeyError, IndexError):
                # Fallback for assets or unexpected structures
                if hasattr(context, "asset") and context.asset:
                    context.asset.name = self.name

        self.report({'INFO'}, f"Rig renamed to: {self.name}")
        return {'FINISHED'}

def register():
    U.register_class(OP_rig_rename)

def unregister():
    U.unregister_class(OP_rig_rename)
