import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from .lib import (
    SACR7_UI2_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs
)

class SACR7_UI2_sui_head(SACR7_UI2_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_head").panel
    bl_label = "Head"
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        mainProp = rig_bones[ConfigObjs.main]

        panel = self.layout
        p_row = panel.row()
        p_col = p_row.column(align=True)
        p_col.prop(mainProp, '["Face Toggle"]',
                   text="Enable Face",
                   toggle=True,
                   icon="HIDE_ON" if mainProp["Face Toggle"] is False else "HIDE_OFF")


classes = [
    SACR7_UI2_sui_head,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
