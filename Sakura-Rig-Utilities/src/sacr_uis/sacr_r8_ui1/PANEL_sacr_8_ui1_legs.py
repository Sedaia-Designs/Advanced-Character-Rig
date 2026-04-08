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

class SEDAIA_PT_SACR8_sui_legConfig(SACR8_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_label = "Legs"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_leg").panel
    bl_order = 3

    def draw(self, context):
        # Variables and Data
        rig = context.active_object
        rig_bones = rig.pose.bones

        legProp = rig_bones[ConfigObjs.leg]

        # UI Layout
        panel = self.layout

        p_row = panel.row()
        p_row.label(text="Style")
        p_row = panel.row()
        p_row.prop(legProp, '["SmoothBends"]', toggle=True, text="Smooth Bend")
        b_row = panel.row()
        b_row.prop(legProp, '["FemaleDeformWeight"]',
                   text="Female Deforms", slider=True)

        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.label(text="Ankle Type")
        p_row = panel.row()
        p_row.prop(legProp, 'AnkleType', expand=True)

        panel.separator(type="LINE")
        p_row = panel.row()
        p_row.label(text="Controllability")
        p_row = panel.row()
        p_row.label(text="IK Settings")
        p_row = panel.row(align=True)
        p_col = p_row.column(heading="Left", align=True)
        p_col.prop(legProp, '["LegIK"]', slider=True, index=0, text="IK")
        p_col.prop(legProp, '["LegStretchIK"]',
                   slider=True, index=0, text="Stretch")
        p_col.prop(legProp, '["AnkleIK"]', slider=True,
                   index=0, text="Ankle IK")

        p_col = p_row.column(heading="Right", align=True)
        p_col.prop(legProp, '["LegIK"]', slider=True, index=1, text="IK")
        p_col.prop(legProp, '["LegStretchIK"]',
                   slider=True, index=1, text="Stretch")
        p_col.prop(legProp, '["AnkleIK"]', slider=True,
                   index=1, text="Ankle IK")

classes = [
    SEDAIA_PT_SACR8_sui_legConfig,
]

# Registering AnkleType properties globally on PoseBone
def register_props():
    T.PoseBone.AnkleType = P.EnumProperty(
        name="Ankle Type",
        description="Ankle Type for the Left Leg",
        items=[
            ("0", "Sharp", "Angular Style"),
            ("1", "Smooth", "Bendy Style")
        ]
    )

def unregister_props():
    try:
        del T.PoseBone.AnkleType
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
