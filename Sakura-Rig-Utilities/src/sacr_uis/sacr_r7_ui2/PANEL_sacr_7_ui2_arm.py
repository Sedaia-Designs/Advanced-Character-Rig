import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs
)

class SACR7_UI2_sui_arm(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Arm"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_arm").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 2

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        mainProp = rig_bones[ConfigObjs.main]
        props = rig.sacr_r7_ui2_props

        panel = self.layout
        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.label(text="Arm Type")
        p_row = panel.row()
        p_row.prop(props, 'arm_type', expand=True)

        panel.separator(type="LINE")
        p_row = panel.row()
        p_row.label(text="Controllability")
        p_row = panel.row()
        p_row.label(text="IK Settings")
        p_row = panel.row(align=True)
        p_col = p_row.column(heading="Left", align=True)
        p_col.prop(mainProp, '["Arm IK"]', slider=True, index=0, text="IK")
        p_col.prop(mainProp, '["Arm Stretch"]', slider=True, index=0, text="Stretch")
        p_col.prop(mainProp, '["Arm Wrist IK"]', slider=True, index=0, text="Wrist IK")

        p_col = p_row.column(heading="Right", align=True)
        p_col.prop(mainProp, '["Arm IK"]', slider=True, index=1, text="IK")
        p_col.prop(mainProp, '["Arm Stretch"]', slider=True, index=1, text="Stretch")
        p_col.prop(mainProp, '["Arm Wrist IK"]', slider=True, index=1, text="Wrist IK")


classes = [
    SACR7_UI2_sui_arm,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
