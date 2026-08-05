import bpy.utils as U

from .lib import enums, types
from ...sru_lib import ID, ui as global_ui, image


def toggle_collection(parent_ui, context, prop, label="Collection"):
    # Panel Variables
    collection_inst = context.active_object.pose.bones["PythonConfig.Objects"].get(prop)
    inst_toggle = parent_ui.operator(
        ID("toggle_collection").operator,
        text=label,
        depress=not collection_inst.hide_viewport,
        icon=(
            "RESTRICT_VIEW_ON" if collection_inst.hide_viewport else "RESTRICT_VIEW_OFF"
        ),
    )
    inst_toggle.collection = collection_inst.name


def armor_material_panel(parent_ui, props, materials, section):
    armor_enum = {  # (Toggle Index, Material Index)
        "Helmet": (0, "armor_helmet"),
        "Chestplate": (1, "armor_chestplate"),
        "Leggings": (2, "armor_leggings"),
        "Boots": (3, "armor_boots"),
    }
    armor_section = armor_enum[section]
    material = materials.get(armor_enum[section][1]).node_tree.nodes[
        f"{section}_Shader"
    ]

    row = parent_ui.row(align=True)
    row.prop(
        props, '["Armor Toggle"]', index=armor_section[0], text=section, toggle=True
    )
    row2 = row.row(align=True)
    row2.enabled = props["Armor Toggle"][armor_section[0]]
    row2.prop(material.inputs["Tier"], "default_value", text="")

    if props["Armor Toggle"][armor_section[0]]:
        mat_column = parent_ui.box().column(align=True)
        mat_column.label(text="Material")
        input = "IOR"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Metalic"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Specular"
        mat_column.prop(material.inputs[input], "default_value", text=input)

        input = "Roughness"
        mat_column.prop(material.inputs[input], "default_value", text=input)
        mat_column.separator(type="SPACE")
        box = mat_column.box()
        mat = material.inputs["Enchant"]
        box.prop(
            mat,
            "default_value",
            text="Enchanted",
            toggle=True,
            icon="CHECKBOX_HLT" if mat.default_value else "CHECKBOX_DEHLT",
        )
        if mat.default_value:
            input = "Strength"
            box.prop(material.inputs[input], "default_value", text=input)

            input = "Glint Offset"
            box.prop(material.inputs["Location"], "default_value", text=input)


class PT_Main(types.SACR_UI73_Panel):
    bl_label = "Main Panel"
    bl_order = 0
    bl_idname = ID("r750_main").panel

    def draw(self, context):

        # Panel Variables
        obj = context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all

        main = pose["Rig_Properties"]
        face = pose["Face_Properties"]
        eyebrow = pose["Eyebrow_Properties"]
        eyes = pose["Eye_Properties"]
        mouth = pose["Mouth_Properties"]
        python = pose["PythonConfig.Objects"]
        py_panel_helper = pose["PythonConfig.PanelHelper"]
        root = pose["SACR_Root"]

        rig_feature_set = enums.feature_set[obj.data["feature_set"]]

        py_materials = pose["PythonConfig.Materials"]

        skin = py_materials.get("skin").node_tree.nodes["Skin_Texture"].image

        # Panel Layout
        ui = self.layout

        if rig_feature_set == "Python":
            ui.prop(
                collections["Python"], "is_visible", text="Python Config", icon="PLUGIN"
            )

        ui.prop(
            root.constraints["NormalizeScale"],
            "enabled",
            text="Reset Rig Scale",
            invert_checkbox=True,
            icon=(
                "CHECKBOX_DEHLT"
                if root.constraints["NormalizeScale"].enabled
                else "CHECKBOX_HLT"
            ),
        )

        ui.label(text="Skin Texture")
        row = ui.row(align=True)
        row.operator(
            ID("image_pack").operator,
            icon="PACKAGE" if image.is_packed(skin) else "UGLYPACKAGE",
            text="",
        ).path = skin.name

        filepath_ui = row.row(align=True)
        filepath_ui.enabled = not image.is_packed(skin)
        filepath_ui.prop(skin, "filepath", text="")
        filepath_ui.operator(
            ID("image_reload").operator, icon="FILE_REFRESH", text=""
        ).path = skin.name

        row = ui.row(align=True)
        toggle_collection(row, context, prop="HatLayer", label="Show Jacket Layer")
        toggle_collection(
            row, context, prop="ExtrudeMeshes", label="Show Extrude Heads"
        )

        ui.separator(type="LINE")

        ui.label(text="Extras")

        col = ui.column(align=True)
        col.prop(
            collections["Flip"],
            "is_visible",
            text="Flip Bone",
            toggle=True,
            icon="HIDE_OFF" if collections["Flip"].is_visible else "HIDE_ON",
        )

        col.prop(
            main,
            '["Wireframe Bones"]',
            toggle=True,
            icon="CHECKBOX_HLT" if main["Wireframe Bones"] else "CHECKBOX_DEHLT",
        )

        col.separator(type="LINE")

        if rig_feature_set != "Lite":
            col.prop(
                main,
                '["Long Hair Rig"]',
                text="Long Hair",
                toggle=True,
                icon="HIDE_OFF" if main["Long Hair Rig"] else "HIDE_ON",
            )

            hair_box = col.box()
            hair_box.enabled = main["Long Hair Rig"]
            hair_box.prop(
                collections["Hair_Adv"],
                "is_visible",
                text="Hair Extra Controls",
                icon="HIDE_OFF" if collections["Hair_Adv"].is_visible else "HIDE_ON",
            )

            ui.separator(type="LINE")
            ui.label(text="Deformations")

            col = ui.column(align=True)
            row = col.row(align=True)
            row.prop(
                main,
                '["Show Lattices"]',
                index=0,
                text="Body Lattices",
                icon="HIDE_OFF" if main["Show Lattices"][0] else "HIDE_ON",
            )
            row.prop(
                main,
                '["Show Lattices"]',
                index=1,
                text="Eyelash Lattices",
                icon="HIDE_OFF" if main["Show Lattices"][1] else "HIDE_ON",
            )

            ui.prop(main, '["Female Curves"]', text="Female Curvature")

            ui.separator(type="LINE")

        # Sub Panels
        ui.label(text="Sections")

        panel_arms(ui, py_panel_helper, main)

        ui.separator(type="LINE")

        panel_legs(ui, py_panel_helper, main)

        if rig_feature_set != "Lite":
            ui.separator(type="LINE")

            armor = global_ui.sub_panel(
                ui, py_panel_helper, prop="ArmorPanel", label="Armor"
            )
            if armor:
                armor_enum = (
                    "Helmet",
                    "Chestplate",
                    "Leggings",
                    "Boots",
                )
                for item in armor_enum:
                    armor_material_panel(armor, main, py_materials, item)


def panel_arms(parent_ui, panel_helper, props):
    arms = global_ui.sub_panel(parent_ui, panel_helper, prop="ArmPanel", label="Arms")
    if arms:
        row = arms.row()
        row.label(text="Arm Type")
        row = arms.row(align=True)
        row.prop(props, '["Arm Type"]')

        arms.separator(type="SPACE")

        row = arms.row(align=True)
        col = row.column(align=True)
        col.label(text="Left")
        col.prop(props, '["Arm IK"]', index=0, text="IK")
        col.prop(props, '["Arm Stretch"]', index=0, text="Stretch")
        col.prop(props, '["Arm Wrist IK"]', index=0, text="Wrist IK")

        col = row.column(align=True)
        col.label(text="Right")
        col.prop(props, '["Arm IK"]', index=1, text="IK")
        col.prop(props, '["Arm Stretch"]', index=1, text="Stretch")
        col.prop(props, '["Arm Wrist IK"]', index=1, text="Wrist IK")


def panel_legs(panel_ui, panel_helper, props):
    legs = global_ui.sub_panel(panel_ui, panel_helper, prop="LegPanel", label="Legs")
    if legs:
        row = legs.row(align=True)
        col = row.column(align=True)
        col.label(text="Left")
        col.prop(props, '["Leg FK"]', index=0, text="IK")
        col.prop(props, '["Leg Stretch"]', index=0, text="Stretch")

        col = row.column(align=True)
        col.label(text="Right")
        col.prop(props, '["Leg FK"]', index=1, text="IK")
        col.prop(props, '["Leg Stretch"]', index=1, text="Stretch")


def register():
    U.register_class(PT_Main)


def unregister():
    U.unregister_class(PT_Main)
