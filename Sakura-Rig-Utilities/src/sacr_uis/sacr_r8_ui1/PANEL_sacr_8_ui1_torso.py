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

class SEDAIA_PT_SACR8_sui_torsoConfig(SACR8_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_label = "Torso"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_torso").panel
    bl_order = 1

    def draw(self, context):
        # Variables and Data
        rig = context.active_object
        rig_bones = rig.pose.bones

        # mainProp = rig_bones["Properties.RigMain"]
        torsoProp = rig_bones[ConfigObjs.torso]

        # UI Layout
        panel = self.layout

        p_row = panel.row()
        p_row.label(text="Style")
        p_row = panel.row()
        p_row.prop(torsoProp, '["FemaleDeformWeight"]',
                   text="Female Deforms", slider=True)

classes = [
    SEDAIA_PT_SACR8_sui_torsoConfig,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
