import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from ...preferences import Prefixer
from .lib import (
    SACR8_UI1_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs,
)

class SEDAIA_PT_SACR8_sui_armConfig(SACR8_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_label = "Arms"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_arm").panel
    bl_order = 2

    def draw(self, context):
        # Variables and Data
        rig = context.active_object
        rig_bones = rig.pose.bones

        armProp = rig_bones[ConfigObjs.arm]

        # UI Layout
        panel = self.layout

        p_row = panel.row()
        p_row.label(text="Style")
        p_row = panel.row()
        p_row.prop(armProp, '["SmoothBends"]', toggle=True, text="Smooth Bend")

        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.label(text="Arm Type")
        p_row = panel.row()
        p_row.prop(armProp, 'ArmType', expand=True)

        panel.separator(type="LINE")
        p_row = panel.row()
        p_row.label(text="Controllability")
        p_row = panel.row()
        p_row.label(text="IK Settings")
        p_row = panel.row(align=True)
        p_col = p_row.column(heading="Left", align=True)
        p_col.prop(armProp, '["ArmIK"]', slider=True, index=0, text="IK")
        p_col.prop(armProp, '["ArmStretchIK"]',
                   slider=True, index=0, text="Stretch")
        p_col.prop(armProp, '["WristIK"]', slider=True,
                   index=0, text="Wrist IK")

        p_col = p_row.column(heading="Right", align=True)
        p_col.prop(armProp, '["ArmIK"]', slider=True, index=1, text="IK")
        p_col.prop(armProp, '["ArmStretchIK"]',
                   slider=True, index=1, text="Stretch")
        p_col.prop(armProp, '["WristIK"]', slider=True,
                   index=1, text="Wrist IK")

classes = [
    SEDAIA_PT_SACR8_sui_armConfig,
]

# Registering ArmType properties globally on PoseBone
def register_props():
    T.PoseBone.ArmType = P.EnumProperty(
        name="Arm Type",
        description="Select your Arm Dimension",
        default="0",
        items=[
            ("0", "Standard", "Standard Arm Style, formerly called Steve Arms"),
            ("1", "Slim", "Slim Arm Style, formerly called Steve Arms"),
            ("2", "Super-Slim",
             "Super Slim Arm style are a 3x3 version not available in Minecraft")
        ]
    )

def unregister_props():
    try:
        del T.PoseBone.ArmType
    except AttributeError:
        pass

def register():
    register_props()
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
    unregister_props()
