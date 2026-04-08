import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI1_Face_Panel_Base,
    mesh_mat_obj,
    id_prop,
    id_str,
)

class SEDAIA_PT_sacr_7_ui_1_eyebrows(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "Eyebrows Settings"
    bl_parent_id = Prefixer("sacr_7_ui_1_face_main").panel
    bl_idname = Prefixer("sacr_7_ui_1_eyebrows").panel
    bl_order = 0

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones

        eyebrows = bone["Eyebrow_Properties"]
        rig_child = obj.children_recursive

        if obj.data.get(id_prop) == id_str[0]:
            matObj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)

            eyebrowMat = matObj.material_slots[6].material.node_tree.nodes['Node']
            eyebrowGrad = eyebrowMat.inputs['Gradient'].default_value
            eyebrowSplit = eyebrowMat.inputs['Split Color'].default_value

        # UI
        layout = self.layout

        row = layout.row()
        col = row.column(align=True)
        col.prop(eyebrows, '["Depth"]', slider=True)
        col.prop(eyebrows, '["Width"]', slider=True)
        col.prop(eyebrows, '["Thickness"]', slider=True)

        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="More Controls")
        row = layout.row(align=True)
        row.prop(eyebrows, '["Extended Controls"]',
                 index=0, text="Left", slider=False)
        row.prop(eyebrows, '["Extended Controls"]',
                 index=1, text="Right", slider=False)

        if obj.data.get(id_prop) == id_str[0]:
            row = layout.row()
            row.label(text='Eyebrow Colors')

            row = layout.row(align=True)

            colLeft = row.column(heading="", align=True)
            colLeftRow1 = colLeft.row(align=True)
            colLeftRow2 = colLeft.row(align=True)
            colRight = row.column(heading="", align=True)
            colRightRow1 = colRight.row(align=True)
            colRightRow2 = colRight.row(align=True)
            colLeftRow1.prop(
                eyebrowMat.inputs['L.Color In'], "default_value", text="")
            colLeft.prop(
                eyebrowMat.inputs['Gradient'], "default_value", text='Gradient', toggle=True)
            colRight.prop(
                eyebrowMat.inputs['Split Color'], "default_value", text='Split', toggle=True)

            colLeftRow2.enabled = eyebrowGrad
            colLeftRow2.prop(
                eyebrowMat.inputs['L.Color Out'], "default_value", text="")

            colRightRow1.enabled = eyebrowSplit
            colRightRow1.prop(
                eyebrowMat.inputs['R.Color In'], "default_value", text="")

            colRightRow2.enabled = eyebrowSplit and eyebrowGrad
            colRightRow2.prop(
                eyebrowMat.inputs['R.Color Out'], "default_value", text="")


classes = [
    SEDAIA_PT_sacr_7_ui_1_eyebrows,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
