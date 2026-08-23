# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ..sru_lib import ID
from ..sru_lib import types


# Write Code Here
class PT_Rig_Manager(T.Panel):
    bl_label = "Rig Manager"
    bl_idname = ID("rig_manager").panel
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rig Manager"

    def draw(self, context):

        scene = context.scene

        layout = self.layout
        layout.label(text="Rig Manager Test")
        layout.operator(ID("download_sacr_manifest").operator)
        layout.template_list(
            ID("rig_list").list, # listtype_name
            "", # list_id, leave Empty
            scene, # dataptr, Data from which to take the Collection Property
            "sacr_rigs", # propname, Identifier of the Collection propery in data, never None
            scene, # active_dataptr, Data from which to take the integer property, index of the active item (never None)
            "selected_rig", # active_propname, Identifier of the integer property in active_data, index of the active item (never None)
            rows=2,
            maxrows=6,
            columns=2
        )

# Register and unregister classes
classes = (PT_Rig_Manager,)


def register():
    for cls in classes:
        U.register_class(cls)


def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
