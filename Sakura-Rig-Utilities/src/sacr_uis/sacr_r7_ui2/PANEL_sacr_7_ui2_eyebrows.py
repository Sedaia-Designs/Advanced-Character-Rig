import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Face_Panel_Base,
    rig_ver,
    ui_ver,
    config_objs,
)

class SACR7_UI2_sui_eyebrows(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Eyebrows"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyebrows").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_data = rig.data
        rig_bones = rig.pose.bones
        rig_bc = rig_data.collections_all
        eyebrowProp = rig_bones[config_objs["eyebrows"]]
        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=config_objs['materials'])
        eyebrowMat = mat_obj.material_slots[6].material.node_tree.nodes['Node']
        eyebrowGrad = eyebrowMat.inputs['Gradient'].default_value
        eyebrowSplit = eyebrowMat.inputs['Split Color'].default_value

        panel = self.layout
        row = panel.row()
        row.label(text="Controller Toggle")
        row = panel.row()
        col = row.column()

        # Left Eyebrow
        row = col.row(align=True)
        row.prop(rig_bc["Eyebrow_Left_Simplified"], 'is_visible',
                 text="Left Basic",
                 icon="HIDE_ON" if rig_bc["Eyebrow_Left_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eyebrow_Left_Simplified'].is_visible
        row_e.prop(rig_bc["Eyebrow_Left_Advanced"], 'is_visible',
                   text="Left Advanced",
                   icon="HIDE_ON" if rig_bc["Eyebrow_Left_Advanced"].is_visible is False else "HIDE_OFF")

        # Right Eyebrow
        row = col.row(align=True)
        row.prop(rig_bc["Eyebrow_Right_Simplified"], 'is_visible',
                 text="Right Basic",
                 icon="HIDE_ON" if rig_bc["Eyebrow_Right_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eyebrow_Right_Simplified'].is_visible
        row_e.prop(rig_bc["Eyebrow_Right_Advanced"], 'is_visible',
                   text="Right Advanced",
                   icon="HIDE_ON" if rig_bc["Eyebrow_Right_Advanced"].is_visible is False else "HIDE_OFF")

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text="Options", icon="PROPERTIES")

        row = panel.row()
        col = row.column(align=True)
        col.prop(eyebrowProp, '["Depth"]', slider=True)
        col.prop(eyebrowProp, '["Width"]', slider=True)
        col.prop(eyebrowProp, '["Thickness"]', slider=True)

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text='Colors', icon="MOD_COLOR_BALANCE")

        row = panel.row(align=True)
        colLeft = row.column(heading="", align=True)
        colLeftRow1 = colLeft.row(align=True)
        colLeftRow2 = colLeft.row(align=True)
        colRight = row.column(heading="", align=True)
        colRightRow1 = colRight.row(align=True)
        colRightRow2 = colRight.row(align=True)

        colLeftRow1.prop(eyebrowMat.inputs['L.Color In'], "default_value", text="")
        colLeft.prop(eyebrowMat.inputs['Gradient'], "default_value", text='Gradient', toggle=True)
        colRight.prop(eyebrowMat.inputs['Split Color'], "default_value", text='Split', toggle=True)

        colLeftRow2.enabled = eyebrowGrad
        colLeftRow2.prop(eyebrowMat.inputs['L.Color Out'], "default_value", text="")

        colRightRow1.enabled = eyebrowSplit
        colRightRow1.prop(eyebrowMat.inputs['R.Color In'], "default_value", text="")

        colRightRow2.enabled = eyebrowSplit and eyebrowGrad
        colRightRow2.prop(eyebrowMat.inputs['R.Color Out'], "default_value", text="")


classes = [
    SACR7_UI2_sui_eyebrows,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
