"""Toggle the object collection referenced by an R7.5 rig."""

import bpy
import bpy.props as P
import bpy.types as T
import bpy.utils as U

from ..ui import ID, RIG_ID_GROUP


class OT_toggle_collection(T.Operator):
    bl_idname = ID("toggle_collection").operator_for(RIG_ID_GROUP)
    bl_label = "Toggle Collection"
    bl_options = {"REGISTER", "UNDO"}

    collection: P.StringProperty()

    @classmethod
    def poll(cls, context):
        """Return whether the current Blender context supports this UI element."""
        obj = context.active_object
        return bool(obj and obj.type == "ARMATURE")

    def execute(self, context):
        """Apply this operator to the current Blender context."""
        obj = context.active_object
        references = obj.pose.bones.get("PythonConfig.Objects")
        collection = bpy.data.collections.get(self.collection)
        if references is None or collection is None or collection not in references.values():
            self.report({"ERROR"}, "Rig collection is unavailable")
            return {"CANCELLED"}
        collection.hide_viewport = not collection.hide_viewport
        collection.hide_render = collection.hide_viewport
        return {"FINISHED"}


def register():
    """Register this module's Blender classes."""
    U.register_class(OT_toggle_collection)


def unregister():
    """Unregister this module's Blender classes."""
    U.unregister_class(OT_toggle_collection)
