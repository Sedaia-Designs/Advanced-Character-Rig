import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from .lib import (
    SACR7_UI2_Face_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs
)

class SACR7_UI2_sui_face(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Face"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_head").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        faceProp = rig_bones[ConfigObjs.face]

        panel = self.layout
        p_row = panel.row()
        p_row.label(text="Face Controls")

        p_row = panel.row(align=True)
        p_row.prop(faceProp, '["Face | UV"]',
                   text="Face Auto-UV", toggle=True,
                   icon="HIDE_ON" if faceProp["Face | UV"] is False else "HIDE_OFF")


classes = [
    SACR7_UI2_sui_face,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
