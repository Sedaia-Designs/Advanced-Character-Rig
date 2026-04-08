import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI1_Panel_Base,
    mesh_mat_obj,
    id_prop,
    id_str,
)

class SEDAIA_PT_sacr_7_ui_1_legs(SACR7_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_legs").panel
    bl_label = "Leg Settings"
    bl_order = 2

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones
        main = bone["Rig_Properties"]

        # UI
        layout = self.layout
        row = layout.row(align=True)
        leg = 0
        col = row.column(heading="Left")
        col.prop(main, '["Leg FK"]', index=leg, text="FK", slider=True)
        col.prop(main, '["Leg Stretch"]', index=leg,
                 text="Stretch", slider=True)

        leg = 1
        col = row.column(heading="Right")
        col.prop(main, '["Leg FK"]', index=leg, text="FK", slider=True)
        col.prop(main, '["Leg Stretch"]', index=leg,
                 text="Stretch", slider=True)


classes = [
    SEDAIA_PT_sacr_7_ui_1_legs,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
