import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI1_Panel_Base,
    mesh_mat_obj,
    id_prop,
    id_str,
)

class SEDAIA_PT_sacr_7_ui_1_bone_groups(SACR7_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_bone_groups").panel
    bl_label = "Bone Collections"
    bl_order = 0

    def draw(self, context):
        # Define UI
        layout = self.layout
        row = layout.row()
        row.template_bone_collection_tree()


classes = [
    SEDAIA_PT_sacr_7_ui_1_bone_groups,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
