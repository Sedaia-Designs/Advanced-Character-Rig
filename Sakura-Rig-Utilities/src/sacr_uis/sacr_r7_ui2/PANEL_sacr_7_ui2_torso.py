import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Panel_Base,
    rig_ver,
    ui_ver,
    config_objs,
)

class SACR7_UI2_sui_torso(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Torso"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_torso").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 1

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        return context.active_object.data.get('lite', False) is False

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        mainProp = rig_bones[config_objs["main"]]

        panel = self.layout
        p_row = panel.row()
        p_row.label(text="Style")
        p_row = panel.row()
        p_row.prop(mainProp, '["Female Curves"]', text="Female Deforms", slider=True)
        p_row = panel.row()
        p_row.prop(mainProp, '["Long Hair Rig"]', text="Hair Rig")


classes = [
    SACR7_UI2_sui_torso,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
