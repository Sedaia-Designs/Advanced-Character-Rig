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

class SEDAIA_PT_sacr_7_ui_1_arms(SACR7_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_arms").panel
    bl_label = "Arm Settings"
    bl_order = 1

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones
        main = bone["Rig_Properties"]

        # UI
        layout = self.layout
        row = layout.row()
        row.label(text="Properties", icon="PROPERTIES")

        row = layout.row()
        row.prop(main, '["Slim Arms"]', text="Slim Arms")

        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="IK Settings")

        row = layout.row(align=True)
        arm = 0
        col = row.column(heading="Left")
        col.prop(main, '["Arm IK"]', index=arm, text="IK", slider=True)
        col.prop(main, '["Arm Stretch"]', index=arm,
                 text="Stretch", slider=True)
        col.prop(main, '["Arm Wrist IK"]', index=arm,
                 text="Wrist IK", slider=True)

        arm = 1
        col = row.column(heading="Right")
        col.prop(main, '["Arm IK"]', index=arm, text="IK", slider=True)
        col.prop(main, '["Arm Stretch"]', index=arm,
                 text="Stretch", slider=True)
        col.prop(main, '["Arm Wrist IK"]', index=arm,
                 text="Wrist IK", slider=True)


classes = [
    SEDAIA_PT_sacr_7_ui_1_arms,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
