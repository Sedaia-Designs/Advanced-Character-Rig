import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI1_Face_Panel_Base,
    mesh_mat_obj,
    id_prop,
    id_str,
)

class SEDAIA_PT_sacr_7_ui_1_face_main(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "SACR Facerig"
    bl_idname = Prefixer("sacr_7_ui_1_face_main").panel
    bl_order = 1

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones

        main = bone["Rig_Properties"]
        face = bone["Face_Properties"]

        latticeProp = obj.data.get('Show Lattices', False)

        # UI
        layout = self.layout

        row = layout.row()
        row.prop(face, '["Face | UV"]', toggle=True, text="UV projection")
        if latticeProp is not False:
            row.prop(
                main, '["Show Lattices"]', index=1, toggle=True, text="Eyelash Lattice"
            )


classes = [
    SEDAIA_PT_sacr_7_ui_1_face_main,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
