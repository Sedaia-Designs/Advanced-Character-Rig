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

class SACR7_UI2_sui_sclera(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Sclera"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_sclera").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyes").panel
    bl_order = 1

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        props = rig_bones[config_objs["eyes"]]
        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=config_objs['materials'])
        sclera_mat = mat_obj.material_slots[2].material.node_tree
        sclera_shad = sclera_mat.nodes['Sclera_Shader']

        panel = self.layout
        row = panel.row()
        row.label(text="Options", icon="PROPERTIES")
        row = panel.row()
        col = row.column(align=True)
        col.prop(props, '["Sclera Depth"]', text="Eye Depth")

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text="Materials")

        sclera_grad = sclera_shad.inputs[0].default_value
        sclera_het = sclera_shad.inputs[3].default_value

        row = panel.row()
        row.label(text="Colors", icon="MOD_COLOR_BALANCE")
        row = panel.row(align=True)
        colLeft = row.column(heading="", align=True)
        colLeftRow1 = colLeft.row(align=True)
        colLeftRow2 = colLeft.row(align=True)
        colRight = row.column(heading="", align=True)
        colRightRow1 = colRight.row(align=True)
        colRightRow2 = colRight.row(align=True)

        colLeftRow1.prop(sclera_shad.inputs[1], "default_value", text="")
        colLeft.prop(sclera_shad.inputs[0], "default_value", text='Gradient',
                     icon="CHECKBOX_HLT" if sclera_grad is True else "CHECKBOX_DEHLT")
        colRight.prop(sclera_shad.inputs[3], "default_value", text='Hetero',
                      icon="CHECKBOX_HLT" if sclera_het is True else "CHECKBOX_DEHLT")

        colLeftRow2.enabled = sclera_grad
        colLeftRow2.prop(sclera_shad.inputs[2], "default_value", text="")
        colRightRow1.enabled = sclera_het
        colRightRow1.prop(sclera_shad.inputs[4], "default_value", text="")
        colRightRow2.enabled = sclera_het and sclera_grad
        colRightRow2.prop(sclera_shad.inputs[5], "default_value", text="")

        row = panel.row(align=True)
        row.label(text="Reflections", icon="MATERIAL_DATA")
        row = panel.row(align=True)
        col = row.column(align=True)
        col.prop(sclera_shad.inputs[19], 'default_value', text="Metalic")
        col.prop(sclera_shad.inputs[20], 'default_value', text="Specular")
        col.prop(sclera_shad.inputs[21], 'default_value', text="Roughness")
        row = col.row()
        split = row.split(factor=.3)
        split.label(text="Spec Tint")
        split.prop(sclera_shad.inputs[22], 'default_value', text="")

        panel.separator(type="LINE")
        emit_enable = sclera_shad.inputs[31].default_value
        row = panel.row()
        row.label(text="Emission", icon="OUTLINER_OB_LIGHT")
        row = row.row()
        row.alignment = 'RIGHT'
        row.ui_units_x = 3
        row.prop(sclera_shad.inputs[31], 'default_value', text="",
                 icon="CHECKBOX_HLT" if emit_enable is True else "CHECKBOX_DEHLT")

        if emit_enable:
            emit_het = sclera_shad.inputs[34].default_value
            emit_grad = sclera_shad.inputs[35].default_value
            row = panel.row()
            row.prop(sclera_shad.inputs[33], "default_value", text='Split Channels',
                     icon="CHECKBOX_HLT" if sclera_shad.inputs[33].default_value is True else "CHECKBOX_DEHLT")

            if sclera_shad.inputs[33].default_value is True:
                row = panel.row(align=True)
                colLeft = row.column(heading="", align=True)
                colLeftRow1 = colLeft.row(align=True)
                colLeftRow2 = colLeft.row(align=True)
                colRight = row.column(heading="", align=True)
                colRightRow1 = colRight.row(align=True)
                colRightRow2 = colRight.row(align=True)
                colLeftRow1.prop(sclera_shad.inputs[36], "default_value", text="")
                colLeft.prop(sclera_shad.inputs[35], "default_value", text='Gradient',
                             icon="CHECKBOX_HLT" if emit_grad is True else "CHECKBOX_DEHLT")
                colRight.prop(sclera_shad.inputs[34], "default_value", text='Hetero',
                              icon="CHECKBOX_HLT" if emit_het is True else "CHECKBOX_DEHLT")
                colLeftRow2.enabled = emit_grad
                colLeftRow2.prop(sclera_shad.inputs[37], "default_value", text="")
                colRightRow1.enabled = emit_het
                colRightRow1.prop(sclera_shad.inputs[38], "default_value", text="")
                colRightRow2.enabled = emit_het and emit_grad
                colRightRow2.prop(sclera_shad.inputs[39], "default_value", text="")
            else:
                row = panel.row()
                row.prop(sclera_shad.inputs[36], "default_value", text="Strength")


classes = [
    SACR7_UI2_sui_sclera,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
