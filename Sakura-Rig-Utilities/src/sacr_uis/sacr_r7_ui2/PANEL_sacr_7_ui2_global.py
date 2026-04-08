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

class SACR7_UI2_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(cls, context):
        rig_id = f"{rig_info['id']}.Rev_{rig_ver}.UI_{ui_ver}"
        prop_name = "rigID"
        try:
            r = context.active_object
            if r and r.type == "ARMATURE" and r.data:
                return r.data.get(prop_name) == rig_id
            return False
        except (AttributeError, KeyError, TypeError):
            return False


class SACR7_UI2_ui_global(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "SACR Properties"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_col = rig.users_collection[0]
        rig_data = rig.data
        rig_bones = rig.pose.bones
        rig_bc = rig_data.collections_all
        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(
            bl_list=rig_child, query=config_objs['materials'])

        meshCol = utils.lookup_name(
            bl_list=rig_col.children, query="Mesh")

        lite = rig_data.get('lite', False)
        skin = mat_obj.material_slots[0].material.node_tree
        skinTex = skin.nodes["Skin Texture"].image
        mainProp = rig_bones[config_objs['main']]
        root = rig_bones[config_objs["root_bone"]]

        panel = self.layout

        row = panel.row()
        row.label(text="Utilities")

        row = panel.row(align=True)
        row.prop(rig_data, '["Rig Name"]', text="Rig Name")

        rename = row.operator(Prefixer("rig_rename").operator, icon="FILE_REFRESH", text="")
        rename.name = rig_data.get('Rig Name', "")

        row = panel.row()
        row.label(text="Skin Texture")
        row = panel.row(align=True)
        row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(
            skinTex) else "UGLYPACKAGE", text="").path = skinTex.name
        row = row.row(align=True)
        row.enabled = not utils.is_packed(skinTex)
        row.prop(skinTex, "filepath", text="")
        row.operator(Prefixer("image_reload").operator, icon="FILE_REFRESH",
                     text="").path = skinTex.name

        row = panel.row()
        col = row.column_flow(columns=2, align=True)
        col.prop(rig.pose, "use_mirror_x",
                 icon="MOD_MIRROR", text="Mirror X-Axis")
        col.prop(rig_bc['Properties'], 'is_visible',
                 toggle=True, text="Legacy Properties",
                 icon="HIDE_ON" if rig_bc['Properties'].is_visible is False else "HIDE_OFF")

        if "NormalizeScale" in root.constraints:
            col.prop(
                root.constraints["NormalizeScale"],
                'enabled',
                text="Reset Rig Scale",
                invert_checkbox=True, icon="CHECKBOX_DEHLT")

        if lite is False:
            if meshCol:
                col.prop(meshCol, 'hide_select', text="Restrict Selection")
            col.prop(mainProp, '["Show Lattices"]',
                     index=0,
                     text="Body Lattices",
                     icon="HIDE_ON" if mainProp["Show Lattices"][0] is False else "HIDE_OFF")


class SACR7_UI2_sui_head(SACR7_UI2_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_head").panel
    bl_label = "Head"
    bl_order = 0

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        mainProp = rig_bones[config_objs['main']]

        panel = self.layout
        p_row = panel.row()
        p_col = p_row.column(align=True)
        p_col.prop(mainProp, '["Face Toggle"]',
                   text="Enable Face",
                   toggle=True,
                   icon="HIDE_ON" if mainProp["Face Toggle"] is False else "HIDE_OFF")


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


class SACR7_UI2_sui_arm(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Arm"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_arm").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 2

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        mainProp = rig_bones[config_objs['main']]
        props = rig.sacr_r7_ui2_props

        panel = self.layout
        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.label(text="Arm Type")
        p_row = panel.row()
        p_row.prop(props, 'arm_type', expand=True)

        panel.separator(type="LINE")
        p_row = panel.row()
        p_row.label(text="Controllability")
        p_row = panel.row()
        p_row.label(text="IK Settings")
        p_row = panel.row(align=True)
        p_col = p_row.column(heading="Left", align=True)
        p_col.prop(mainProp, '["Arm IK"]', slider=True, index=0, text="IK")
        p_col.prop(mainProp, '["Arm Stretch"]', slider=True, index=0, text="Stretch")
        p_col.prop(mainProp, '["Arm Wrist IK"]', slider=True, index=0, text="Wrist IK")

        p_col = p_row.column(heading="Right", align=True)
        p_col.prop(mainProp, '["Arm IK"]', slider=True, index=1, text="IK")
        p_col.prop(mainProp, '["Arm Stretch"]', slider=True, index=1, text="Stretch")
        p_col.prop(mainProp, '["Arm Wrist IK"]', slider=True, index=1, text="Wrist IK")


class SACR7_UI2_sui_quick_parent(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Quick Parents"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_quick_parent").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 3

    def draw(self, context):
        panel = self.layout
        rig = context.active_object
        rig_data = rig.data
        rig_bc = rig_data.collections_all

        t_row = panel.row()
        t_row.prop(rig_bc["Quick Parents"], "is_visible", text="QP Show Objects",
                   icon="HIDE_ON" if rig_bc["Quick Parents"].is_visible is False else "HIDE_OFF")

        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=True)
        p_col.prop(rig_bc["QP.Head"], "is_visible", text="Head",
                   icon="HIDE_ON" if rig_bc["QP.Head"].is_visible is False else "HIDE_OFF")

        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=True)
        p_col.prop(rig_bc["QP.Torso"], "is_visible", text="Torso",
                   icon="HIDE_ON" if rig_bc["QP.Torso"].is_visible is False else "HIDE_OFF")
        d_row = p_col.row(align=True)
        d_row.enabled = rig_bc["QP.Torso"].is_visible
        d_row.prop(rig_bc["QP.Chest"], "is_visible", text="Chest",
                   icon="HIDE_ON" if rig_bc["QP.Chest"].is_visible is False else "HIDE_OFF")
        d_row.prop(rig_bc["QP.Hip"], "is_visible", text="Hips",
                   icon="HIDE_ON" if rig_bc["QP.Hip"].is_visible is False else "HIDE_OFF")
        d_row.prop(rig_bc["QP.Pelvis"], "is_visible", text="Root",
                   icon="HIDE_ON" if rig_bc["QP.Pelvis"].is_visible is False else "HIDE_OFF")

        panel.separator(type="SPACE")
        p_row = panel.row(align=True)
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm L"], "is_visible", text="Left Arm",
                   icon="HIDE_ON" if rig_bc["QP.Arm L"].is_visible is False else "HIDE_OFF")
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm L"].is_visible
        d_col.prop(rig_bc["QP.Shoulder L"], "is_visible", text="Shoulder",
                   icon="HIDE_ON" if rig_bc["QP.Shoulder L"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Forearm L"], "is_visible", text="Forearm",
                   icon="HIDE_ON" if rig_bc["QP.Forearm L"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Hand L"], "is_visible", text="Hand",
                   icon="HIDE_ON" if rig_bc["QP.Hand L"].is_visible is False else "HIDE_OFF")

        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm R"], "is_visible", text="Right Arm",
                   icon="HIDE_ON" if rig_bc["QP.Arm R"].is_visible is False else "HIDE_OFF")
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm R"].is_visible
        d_col.prop(rig_bc["QP.Shoulder R"], "is_visible", text="Shoulder",
                   icon="HIDE_ON" if rig_bc["QP.Shoulder R"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Forearm R"], "is_visible", text="Forearm",
                   icon="HIDE_ON" if rig_bc["QP.Forearm R"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Hand R"], "is_visible", text="Hand",
                   icon="HIDE_ON" if rig_bc["QP.Hand R"].is_visible is False else "HIDE_OFF")


class SACR7_UI2_sui_armor(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Armor"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_armor").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 4

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        return context.active_object.data.get('lite', False) is False

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        rig_child = rig.children_recursive
        mat_obj = utils.lookup_name(bl_list=rig_child, query=config_objs['materials'])
        mainProp = rig_bones[config_objs["main"]]

        panel = self.layout
        col = panel.column(align=True)

        armor_parts = [
            ("Helmet", 8),
            ("Chestplate", 9),
            ("Leggings", 10),
            ("Boots", 11)
        ]

        for i, (name, slot_idx) in enumerate(armor_parts):
            row = col.row()
            row.prop(mainProp, '["Armor Toggle"]', index=i, text=name,
                     icon="HIDE_ON" if mainProp["Armor Toggle"][i] is False else "HIDE_OFF")
            
            img = mat_obj.material_slots[slot_idx].material.node_tree.nodes["Armor Texture"].image
            row = col.row(align=True)
            row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(img) else "UGLYPACKAGE", text="").path = img.name
            row_f = row.row(align=True)
            row_f.enabled = not utils.is_packed(img)
            row_f.prop(img, "filepath", text="")
            row.operator(Prefixer("image_reload").operator, icon="FILE_REFRESH", text="").path = img.name
            
            if i < len(armor_parts) - 1:
                col.separator(type='SPACE')
                col.separator(type='LINE')
                col.separator(type='SPACE')

classes = [
    SACR7_UI2_ui_global,
    SACR7_UI2_sui_head,
    SACR7_UI2_sui_torso,
    SACR7_UI2_sui_arm,
    SACR7_UI2_sui_quick_parent,
    SACR7_UI2_sui_armor,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)