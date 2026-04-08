import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from .lib import (
    SACR8_UI1_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs,
)

class SEDAIA_PT_SACR8_sui_headConfig(SACR8_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_label = "Head"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_head").panel
    bl_order = 0

    def draw(self, context):
        # Variables and Data
        rig = context.active_object
        rig_bones = rig.pose.bones

        # mainProp = rig_bones["Properties.RigMain"]
        headProp = rig_bones[ConfigObjs.head]

        # UI Layout
        panel = self.layout

        p_row = panel.row()
        p_row.prop(headProp, '["FaceToggle"]', text="Enable Face", toggle=True)

        p_row = panel.row()
        f_box = p_row.box()
        f_box.enabled = headProp['FaceToggle']

        f_row = f_box.row()
        f_row.label(text="Face Settings")

classes = [
    SEDAIA_PT_SACR8_sui_headConfig,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
