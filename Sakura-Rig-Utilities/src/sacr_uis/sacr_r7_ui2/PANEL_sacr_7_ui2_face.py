import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ...operators.lib import blender_utils as utils
from ...preferences import Prefixer

rig_info = {
    "name": "Sakura's Advanced Character Rig",
    "id": "SACR",
    "version": (7, 4, 1),
}

rig_ver = rig_info['version'][0]
ui_ver = 2

config_objs = {
    "main": "Rig_Properties",
    "face": "Face_Properties",
    "mouth": "Mouth_Properties",
    "eyes": "Eye_Properties",
    "eyebrows": "Eyebrow_Properties",
    "materials": "MaterialEditor",
    "root_bone": "SACR_Root"
}

category = f"{rig_info['id']} R{rig_ver}"

class SACR7_UI2_Face_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(cls, context):
        try:
            obj = context.active_object
            if not (obj and obj.type == "ARMATURE" and obj.pose):
                return False
            face_on = obj.pose.bones["Rig_Properties"]["Face Toggle"]
            return face_on
        except (AttributeError, KeyError, TypeError):
            return False


class SACR7_UI2_sui_face(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Face"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_head").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        faceProp = rig_bones[config_objs["face"]]

        panel = self.layout
        p_row = panel.row()
        p_row.label(text="Face Controls")

        p_row = panel.row(align=True)
        p_row.prop(faceProp, '["Face | UV"]',
                   text="Face Auto-UV", toggle=True,
                   icon="HIDE_ON" if faceProp["Face | UV"] is False else "HIDE_OFF")


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


class SACR7_UI2_sui_eyes(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Eyes"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyes").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_order = 1

    def draw(self, context):
        rig = context.active_object
        rig_data = rig.data
        rig_bc = rig_data.collections_all

        panel = self.layout
        row = panel.row()
        row.label(text="Controller Toggle")
        row = panel.row()
        col = row.column()

        # Left Eye
        row = col.row(align=True)
        row.prop(rig_bc["Eye_Left_Simplified"], 'is_visible',
                 text="Left Basic",
                 icon="HIDE_ON" if rig_bc["Eye_Left_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eye_Left_Simplified'].is_visible
        row_e.prop(rig_bc["Eye_Left_Advanced"], 'is_visible',
                   text="Left Advanced",
                   icon="HIDE_ON" if rig_bc["Eye_Left_Advanced"].is_visible is False else "HIDE_OFF")

        # Right Eye
        row = col.row(align=True)
        row.prop(rig_bc["Eye_Right_Simplified"], 'is_visible',
                 text="Right Basic",
                 icon="HIDE_ON" if rig_bc["Eye_Right_Simplified"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Eye_Right_Simplified'].is_visible
        row_e.prop(rig_bc["Eye_Right_Advanced"], 'is_visible',
                   text="Right Advanced",
                   icon="HIDE_ON" if rig_bc["Eye_Right_Advanced"].is_visible is False else "HIDE_OFF")


class SACR7_UI2_sui_iris(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Irises"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_iris").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_eyes").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        props = rig_bones[config_objs["eyes"]]
        mainProp = rig_bones[config_objs['main']]
        ui_props = rig.sacr_r7_ui2_props

        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=config_objs['materials'])
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


class SACR7_UI2_sui_mouth(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Mouth"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_mouth").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_order = 2

    def draw(self, context):
        rig = context.active_object
        rig_data = rig.data
        rig_bones = rig.pose.bones
        rig_bc = rig_data.collections_all
        props = rig_bones[config_objs["mouth"]]
        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=config_objs['materials'])
        mouth_back = mat_obj.material_slots[3].material.node_tree.nodes['Material']
        teeth = mat_obj.material_slots[4].material.node_tree.nodes['Material']

        panel = self.layout
        row = panel.row()
        row.label(text="Controller Toggle")
        row = panel.row()
        col = row.column()

        row = col.row(align=True)
        row.prop(rig_bc["Mouth"], 'is_visible', text="Basic",
                 icon="HIDE_ON" if rig_bc["Mouth"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Mouth'].is_visible
        row_e.prop(rig_bc["Mouth_Advanced"], 'is_visible', text="Advanced",
                   icon="HIDE_ON" if rig_bc["Mouth_Advanced"].is_visible is False else "HIDE_OFF")

        row = panel.row()
        row.label(text="Options", icon="PROPERTIES")
        row = panel.row()
        col = row.column(align=True)
        col.prop(props, '["Square Mouth"]', slider=True, text="Square")
        crow = col.row(align=True)
        crow.prop(props, '["Classic Mouth"]', text="Shallow Mouth",
                  icon="CHECKBOX_HLT" if props.get('Classic Mouth', False) is True else "CHECKBOX_DEHLT")
        crow.prop(rig_bc['Molar Controls'], "is_visible", text="Molar Controls",
                  icon="HIDE_OFF" if rig_bc['Molar Controls'].is_visible is True else "HIDE_ON")

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text="Colors", icon="MOD_COLOR_BALANCE")
        row = panel.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.label(text="Inside")
        row.label(text="Teeth")
        row = col.row(align=True)
        row.prop(mouth_back.inputs['Base Color'], "default_value", text="")
        row.prop(teeth.inputs['Base Color'], "default_value", text="")

classes = [
    SACR7_UI2_sui_face,
    SACR7_UI2_sui_eyebrows,
    SACR7_UI2_sui_eyes,
    SACR7_UI2_sui_iris,
    SACR7_UI2_sui_sclera,
    SACR7_UI2_sui_mouth,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)
