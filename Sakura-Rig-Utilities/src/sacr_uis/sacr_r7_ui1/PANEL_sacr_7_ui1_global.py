import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ...operators.lib import blender_utils as utils
from ...preferences import Prefixer

rig = "SACR"
rig_ver = 7
ui_ver = 1
category = f"{rig} R{rig_ver}"
id_prop = "sacr_id"
id_str = [
    "SACR.Rev_7",  # SACR R7.3 and Newer
    "sacr_1",  # SACR R7.2.1 and older
]
mesh_mat_obj = "MaterialEditor"

class SEDAIA_PT_sacr_7_ui_1_global(T.Panel):
    bl_idname = Prefixer("sacr_7_ui_1_global").panel
    bl_label = "SACR Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
    bl_order = 0

    @classmethod
    def poll(cls, context):
        try:
            obj = context.active_object
            if obj and obj.type == "ARMATURE" and obj.data:
                armature = obj.data
                return armature.get(id_prop) in id_str
            return False
        except (AttributeError, KeyError, TypeError):
            return False

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


class SEDAIA_PT_sacr_7_ui_1_bone_groups(T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_bone_groups").panel
    bl_label = "Bone Collections"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
    bl_order = 0

    @classmethod
    def poll(cls, context):
        try:
            obj = context.active_object
            if obj and obj.type == "ARMATURE" and obj.data:
                return obj.data.get(id_prop) in id_str
            return False
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        # Define UI
        layout = self.layout
        row = layout.row()
        row.template_bone_collection_tree()


class SEDAIA_PT_sacr_7_ui_1_arms(T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_arms").panel
    bl_label = "Arm Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
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


class SEDAIA_PT_sacr_7_ui_1_legs(T.Panel):
    bl_parent_id = Prefixer("sacr_7_ui_1_global").panel
    bl_idname = Prefixer("sacr_7_ui_1_legs").panel
    bl_label = "Leg Settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category
    bl_order = 2

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones
        main = bone["Rig_Properties"]

        # UI
        layout = self.layout
        row = layout.row(align=True)
        leg = 0
        col = row.column(heading="Left")
        col.prop(main, '["Leg FK"]', index=leg, text="FK", slider=True)
        col.prop(main, '["Leg Stretch"]', index=leg,
                 text="Stretch", slider=True)

        leg = 1
        col = row.column(heading="Right")
        col.prop(main, '["Leg FK"]', index=leg, text="FK", slider=True)
        col.prop(main, '["Leg Stretch"]', index=leg,
                 text="Stretch", slider=True)

classes = [
    SEDAIA_PT_sacr_7_ui_1_global,
    SEDAIA_PT_sacr_7_ui_1_legs,
    SEDAIA_PT_sacr_7_ui_1_arms,
    SEDAIA_PT_sacr_7_ui_1_bone_groups,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)
