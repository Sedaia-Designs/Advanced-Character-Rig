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

class SEDAIA_PT_sacr_7_ui_1_sclera(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "Sclera Material"
    bl_parent_id = Prefixer("sacr_7_ui_1_eyes").panel
    bl_idname = Prefixer("sacr_7_ui_1_sclera").panel
    bl_order = 2

    def draw(self, context):
        obj = context.active_object
        rig_child = obj.children_recursive

        if obj.data.get(id_prop) == id_str[0]:
            matObj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)

        scleraMat = matObj.material_slots[2].material.node_tree.nodes['Node']

        # Material Settings
        scleraGrad = scleraMat.inputs['Gradient'].default_value
        scleraSplit = scleraMat.inputs['Heterochromia'].default_value

        sepaEmitCtrls = scleraMat.inputs['Split Emission Controls'].default_value
        emitGrad = scleraMat.inputs[16].default_value
        emitSplit = scleraMat.inputs[15].default_value

        # UI
        layout = self.layout

        row = layout.row()
        row.label(text="Colors", icon="SHADING_RENDERED")

        row = layout.row(align=True)
        leftCol = row.column(align=True)
        rightCol = row.column(align=True)

        leftCol.prop(scleraMat.inputs["Gradient"],
                     'default_value', text="Gradient", toggle=True)
        rightCol.prop(scleraMat.inputs["Heterochromia"],
                      'default_value', text="Split", toggle=True)

        leftColRow1 = leftCol.row(align=True)
        leftColRow1.prop(
            scleraMat.inputs["Color1.L"], 'default_value', text="")

        if scleraGrad is True:
            leftColRow2 = leftCol.row(align=True)
            leftColRow2.prop(
                scleraMat.inputs["Color2.L"], 'default_value', text="")
        if scleraSplit is True:
            rightColRow1 = rightCol.row(align=True)
            rightColRow1.prop(
                scleraMat.inputs["Color1.R"], 'default_value', text="")

            if scleraGrad is True:
                rightColRow2 = rightCol.row(align=True)
                rightColRow2.prop(
                    scleraMat.inputs["Color2.R"], 'default_value', text="")

        layout.separator(type="LINE")
        row = layout.row(align=True)
        row.label(text="Reflections", icon="MATERIAL_DATA")

        row = layout.row(align=True)
        irisCol = row.column(align=True)
        irisCol.prop(scleraMat.inputs['Metalic'],
                     'default_value', text="Metalic")
        irisCol.prop(scleraMat.inputs['IOR'], 'default_value', text="IOR")
        irisCol.prop(scleraMat.inputs['Specular'],
                     'default_value', text="Specular")
        irisCol.prop(scleraMat.inputs['Roughness'],
                     'default_value', text="Roughness")

        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="Emission", icon="OUTLINER_OB_LIGHT")
        row = layout.row(align=True)
        col = row.column(align=True)
        col.prop(scleraMat.inputs['Emission Mask'],
                 'default_value', text="Toggle")
        col.prop(scleraMat.inputs['Split Emission Controls'],
                 'default_value', text="Split Controls", toggle=True)
        if sepaEmitCtrls is True:
            colRow = col.row(align=True)
            colRow.prop(
                scleraMat.inputs[15], 'default_value', text="Heterochromia", toggle=True)
            colRow.prop(
                scleraMat.inputs[16], 'default_value', text="Gradient", toggle=True)
        row = layout.row(align=True)
        if sepaEmitCtrls is False:
            col = row.column(align=True)
            col.prop(scleraMat.inputs['LT'],
                     'default_value', text="Emission Strength")
        else:
            col = row.column(align=True, heading="Left")
            col.prop(scleraMat.inputs['LT'], 'default_value', text="L Top")
            if emitGrad is True:
                col.prop(scleraMat.inputs['LB'],
                         'default_value', text="L Bottom")
            if emitSplit is True:
                col = row.column(align=True, heading="Right")
                col.prop(scleraMat.inputs['RT'], 'default_value', text="R Top")
                if emitGrad is True:
                    col.prop(scleraMat.inputs['RB'],
                             'default_value', text="R Bottom")


classes = [
    SEDAIA_PT_sacr_7_ui_1_sclera,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
