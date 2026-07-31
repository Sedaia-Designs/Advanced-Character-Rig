# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ..lib import Prefixer

# Write Code Here
class PT_Rig_Manager(T.Panel):
    bl_label = "Rig Manager"
    bl_idname = Prefixer("rig_manager").panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rig Manager"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Rig Manager")
        layout.operator(Prefixer("download_sacr_manifest").operator)


# Register and unregister classes
classes = (
    PT_Rig_Manager,
)


def register():
    for cls in classes:
        U.register_class(cls)


def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
