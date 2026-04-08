import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs
)

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
            bl_list=rig_child, query=ConfigObjs.materials)

        meshCol = utils.lookup_name(
            bl_list=rig_col.children, query="Mesh")

        lite = rig_data.get('lite', False)
        skin = mat_obj.material_slots[0].material.node_tree
        skinTex = skin.nodes["Skin Texture"].image
        mainProp = rig_bones[ConfigObjs.main]
        root = rig_bones[ConfigObjs.root_bone]

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


classes = [
    SACR7_UI2_ui_global,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
