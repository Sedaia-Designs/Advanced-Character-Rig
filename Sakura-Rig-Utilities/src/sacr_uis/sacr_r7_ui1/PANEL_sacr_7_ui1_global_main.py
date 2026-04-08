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

class SEDAIA_PT_sacr_7_ui_1_global(SACR7_UI1_Panel_Base, T.Panel):
    bl_idname = Prefixer("sacr_7_ui_1_global").panel
    bl_label = "SACR Properties"
    bl_order = 0

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        armature = obj.data
        bone = obj.pose.bones
        rig_child = obj.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)

        main = bone["Rig_Properties"]
        layers = armature.collections_all

        lite = armature.get("lite", False)
        latticeProp = armature.get("Show Lattices", False)

        skin = mat_obj.material_slots[0].material.node_tree
        skinTex = skin.nodes["Rig Texture"].image

        # Define UI
        layout = self.layout

        row = layout.row()
        row.label(icon="PROPERTIES")
        row.prop(layers["Properties"], "is_visible",
                 text="Bone Props", toggle=True)

        layout.separator(type="LINE")

        if armature.get(id_prop) == id_str[0]:
            row = layout.row()
            row.label(text="Skin Texture")
            row = layout.row(align=True)
            row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(
                skinTex) else "UGLYPACKAGE", text="").path = skinTex.name
            row = row.row(align=True)
            row.enabled = not utils.is_packed(skinTex)
            row.prop(skinTex, "filepath", text="")
            row.operator(Prefixer("image_reload").operator,
                         icon="FILE_REFRESH", text="").path = skinTex.name

            layout.separator(type="LINE")

        row = layout.row(align=True)
        row.label(text="Rig Settings")
        col = layout.column_flow(columns=2, align=True)
        col.prop(main, '["Wireframe Bones"]', toggle=True,
                 invert_checkbox=True, text="Solid Bones")
        col.prop(layers["Flip"], "is_visible", toggle=True, text="Flip Bone")
        try:
            col.prop(
                layers["Quick Parents"],
                "is_visible",
                toggle=True,
                text="Easy Parenting",
            )
        except (AttributeError, KeyError, TypeError):
            pass
        col.prop(main, '["Face Toggle"]', toggle=True, text="Face Rig")

        col.prop(obj.pose, "use_mirror_x", toggle=True)

        if not lite:
            col.prop(main, '["Long Hair Rig"]', text="Long Hair")

            layout.separator(type="LINE")

            if latticeProp is not False:
                row = layout.row()
                col = row.column()
                col.label(text="Lattice Deforms")
                col.prop(
                    main, '["Show Lattices"]', index=0, toggle=True, text="Show Lattices"
                )

            row = layout.row()
            col = row.column(heading="Presets", align=True)
            col.prop(main, '["Female Curves"]',
                     slider=True, text="Female Deform")

            layout.separator(type="LINE")

            row = layout.row()
            col = row.column(align=True, heading="Armor Toggles")
            col.prop(main, '["Armor Toggle"]', index=0,
                     toggle=True, text="Helmet")
            col.prop(main, '["Armor Toggle"]', index=1,
                     toggle=True, text="Chestplate")
            col.prop(main, '["Armor Toggle"]', index=2,
                     toggle=True, text="Leggings")
            col.prop(main, '["Armor Toggle"]', index=3,
                     toggle=True, text="Boots")


classes = [
    SEDAIA_PT_sacr_7_ui_1_global,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
