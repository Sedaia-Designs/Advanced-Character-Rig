import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Face_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs,
)

class SACR7_UI2_sui_iris(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Irises"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_iris").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyes").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        props = rig_bones[ConfigObjs.eyes]
        mainProp = rig_bones[ConfigObjs.main]
        ui_props = rig.sacr_r7_ui2_props

        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=ConfigObjs.materials)
        iris_mat = mat_obj.material_slots[1].material.node_tree
        iris_shad = iris_mat.nodes['Iris_Shader']
        pupil_tex = iris_mat.nodes['Pupil_Tex'].image
        iris_ramp = iris_mat.nodes['Ramp']

        panel = self.layout
        row = panel.row()
        row.label(text="Options", icon="PROPERTIES")

        row = panel.row(align=True)
        split = row.split(factor=.3)
        split.label(text="Lash Style")
        split.prop(ui_props, 'eyelashes', text="")

        if rig.data.get('lite', False) is False:
            row = panel.row()
            col = row.column(align=True)
            crow = col.row(align=True)
            crow.prop(mainProp, '["Show Lattices"]', index=1, toggle=True, text="Show Lattice",
                      icon="HIDE_ON" if mainProp["Show Lattices"][1] is False else "HIDE_OFF")
            crow.prop(props, '["Eyesparkle"]', text="Eye Sparkles",
                      icon="HIDE_ON" if props["Eyesparkle"] is False else "HIDE_OFF")
            col.prop(props, '["Iris Inset"]', text="Inset Irises")
        else:
            row = panel.row()
            col = row.column(align=True)
            col.prop(props, '["Iris Inset"]', text="Inset Irises")

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text="Materials")

        iris_grad = iris_shad.inputs[0].default_value
        iris_het = iris_shad.inputs[3].default_value

        row = panel.row()
        row.label(text="Colors", icon="MOD_COLOR_BALANCE")
        row = panel.row(align=True)
        colLeft = row.column(heading="", align=True)
        colLeftRow1 = colLeft.row(align=True)
        colLeftRow2 = colLeft.row(align=True)
        colRight = row.column(heading="", align=True)
        colRightRow1 = colRight.row(align=True)
        colRightRow2 = colRight.row(align=True)

        colLeftRow1.prop(iris_shad.inputs[1], "default_value", text="")
        colLeft.prop(iris_shad.inputs[0], "default_value", text='Gradient',
                     icon="CHECKBOX_HLT" if iris_shad.inputs[0].default_value is True else "CHECKBOX_DEHLT")
        colRight.prop(iris_shad.inputs[3], "default_value", text='Hetero',
                      icon="CHECKBOX_HLT" if iris_shad.inputs[3].default_value is True else "CHECKBOX_DEHLT")

        colLeftRow2.enabled = iris_grad
        colLeftRow2.prop(iris_shad.inputs[2], "default_value", text="")
        colRightRow1.enabled = iris_het
        colRightRow1.prop(iris_shad.inputs[4], "default_value", text="")
        colRightRow2.enabled = iris_het and iris_grad
        colRightRow2.prop(iris_shad.inputs[5], "default_value", text="")

        row = panel.row(align=True)
        row.label(text="Reflections", icon="MATERIAL_DATA")
        row = panel.row(align=True)
        col = row.column(align=True)
        col.prop(iris_shad.inputs[19], 'default_value', text="Metalic")
        col.prop(iris_shad.inputs[20], 'default_value', text="Specular")
        col.prop(iris_shad.inputs[21], 'default_value', text="Roughness")
        row = col.row()
        split = row.split(factor=.3)
        split.label(text="Spec Tint")
        split.prop(iris_shad.inputs[22], 'default_value', text="")

        panel.separator(type="LINE")
        emit_enable = iris_shad.inputs[31].default_value
        row = panel.row()
        row.label(text="Emission", icon="OUTLINER_OB_LIGHT")
        row = row.row()
        row.alignment = 'RIGHT'
        row.ui_units_x = 3
        row.prop(iris_shad.inputs[31], 'default_value', text="",
                 icon="CHECKBOX_HLT" if emit_enable is True else "CHECKBOX_DEHLT")

        if emit_enable:
            row = panel.row()
            row.prop(iris_shad.inputs[32], 'default_value', text='Factor')
            row = panel.row()
            row.label(text="Emit Strength")
            emit_het = iris_shad.inputs[34].default_value
            emit_grad = iris_shad.inputs[35].default_value
            row = panel.row(align=True)

            if iris_shad.inputs[33].default_value is True:
                colLeft = row.column(heading="", align=True)
                colLeftRow1 = colLeft.row(align=True)
                colLeftRow2 = colLeft.row(align=True)
                colRight = row.column(heading="", align=True)
                colRightRow1 = colRight.row(align=True)
                colRightRow2 = colRight.row(align=True)
                colLeftRow1.prop(iris_shad.inputs[36], "default_value", text="")
                colLeft.prop(iris_shad.inputs[35], "default_value", text='Gradient',
                             icon="CHECKBOX_HLT" if iris_shad.inputs[35].default_value is True else "CHECKBOX_DEHLT")
                colRight.prop(iris_shad.inputs[34], "default_value", text='Hetero',
                              icon="CHECKBOX_HLT" if iris_shad.inputs[34].default_value is True else "CHECKBOX_DEHLT")
                colLeftRow2.enabled = emit_grad
                colLeftRow2.prop(iris_shad.inputs[37], "default_value", text="")
                colRightRow1.enabled = emit_het
                colRightRow1.prop(iris_shad.inputs[38], "default_value", text="")
                colRightRow2.enabled = emit_het and emit_grad
                colRightRow2.prop(iris_shad.inputs[39], "default_value", text="")
                row = panel.row()
                row.prop(iris_shad.inputs[33], "default_value", text='Split Channels', toggle=True)
            else:
                col = row.column()
                col.prop(iris_shad.inputs[36], "default_value", text="Strength")
                col.prop(iris_shad.inputs[33], "default_value", text='Split Channels', toggle=True)

        row = panel.row(align=True)
        row.label(text="Pupils", icon="SHADING_RENDERED")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.ui_units_x = 3
        row.prop(iris_shad.inputs[40], 'default_value', text="",
                 icon="CHECKBOX_HLT" if iris_shad.inputs[40].default_value is True else "CHECKBOX_DEHLT")

        if iris_shad.inputs[40].default_value is True:
            row = panel.row()
            row.prop(iris_shad.inputs[41], 'default_value', text='')
            row = panel.row(align=True)
            row.prop(iris_shad.inputs[42], 'default_value', text='Opacity')
            row.prop(iris_shad.inputs[43], 'default_value', text='Custom')
            row = panel.row(align=True)
            row.label(text="Pupil Scale")
            row = panel.row(align=True)
            row.prop(iris_shad.inputs['Size X'], 'default_value', text='X', slider=True)
            row.prop(iris_shad.inputs['Size Y'], 'default_value', text='Y', slider=True)

            if iris_shad.inputs[43].default_value > 0:
                panel.separator(type="LINE")
                row = panel.row()
                row.label(text="Pupil Texture")
                row = panel.row(align=True)
                row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(
                    pupil_tex) else "UGLYPACKAGE", text="").path = pupil_tex.name
                row = row.row(align=True)
                row.enabled = not utils.is_packed(pupil_tex)
                row.prop(pupil_tex, "filepath", text="")
                row.operator(Prefixer("image_reload").operator, icon="FILE_REFRESH",
                             text="").path = pupil_tex.name

                pupil_box = panel.box()
                pupil_box.label(text="Pupil Color Ramp")
                pupil_box.template_color_ramp(iris_ramp, 'color_ramp', expand=True)


classes = [
    SACR7_UI2_sui_iris,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
