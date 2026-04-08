import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Face_Panel_Base,
    rig_ver,
    ui_ver,
    config_objs,
)

class SACR7_UI2_sui_eyes(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Eyes"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyes").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_order = 1

    def draw(self, context):
        rig = context.active_object
        rig_data = rig.data
        rig_bc = rig_data.collections_all

        panel = self.layout
        row = panel.row()
        row.label(text="Controller Toggle")
        row = panel.row()
        col = row.column()

        # Left Eye
        row = col.row(align=True)
        row.prop(rig_bc["Eye_Left_Simplified"], 'is_visible',
                 text="Left Basic",
                 icon="HIDE_ON" if rig_bc["Eye_Left_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eye_Left_Simplified'].is_visible
        row_e.prop(rig_bc["Eye_Left_Advanced"], 'is_visible',
                   text="Left Advanced",
                   icon="HIDE_ON" if rig_bc["Eye_Left_Advanced"].is_visible is False else "HIDE_OFF")

        # Right Eye
        row = col.row(align=True)
        row.prop(rig_bc["Eye_Right_Simplified"], 'is_visible',
                 text="Right Basic",
                 icon="HIDE_ON" if rig_bc["Eye_Right_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eye_Right_Simplified'].is_visible
        row_e.prop(rig_bc["Eye_Right_Advanced"], 'is_visible',
                   text="Right Advanced",
                   icon="HIDE_ON" if rig_bc["Eye_Right_Advanced"].is_visible is False else "HIDE_OFF")


classes = [
    SACR7_UI2_sui_eyes,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
