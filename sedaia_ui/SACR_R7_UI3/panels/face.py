import bpy.utils as U

from ..ui import ui, enums, types
from ..ui import ID, RIG_ID_GROUP, ui as global_ui


class PT_Face(types.SACR_UI750_Panel):
    """
    Represents a Face Options panel in the user interface.

    This class provides a panel for configuring face options within a
    specific user interface system. It allows customization of multiple
    face-related properties, including UV projection, eyelashes,
    eyebrows, iris, sclera, and mouth through an organized and toggled
    layout. The presence and behavior of certain features depend on the
    feature set defined for the active object.

    Attributes:
        bl_idname (str): Identifier for the panel.
        bl_label (str): Label displayed for the panel.
        bl_order (int): Defines the order of the panel in the UI.

    Methods:
        draw(context): Renders the panel's layout and properties based on
        the current context.
    """

    bl_idname = ID("face").panel_for(RIG_ID_GROUP)
    bl_label = "Face Options"
    bl_order = 1

    def draw(self, context):

        # Panel Variables
        """Draw this UI element for the current Blender context."""
        obj = context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all
        main = pose["Rig_Properties"]
        face = pose["Face_Properties"]
        eyes = pose["Eye_Properties"]
        python = pose["PythonConfig.Objects"]

        rig_feature_set = enums.feature_set[obj.data["feature_set"]]

        py_materials = pose["PythonConfig.Materials"]
        py_panel_helper = pose["PythonConfig.PanelHelper"]

        # Panel Layout
        layout = self.layout
        layout.prop(main, '["Face Toggle"]', toggle=True)

        if main["Face Toggle"]:
            layout.separator(type="LINE")

            layout.prop(
                face, '["UV Projection"]', text="Face UV Projection", toggle=True
            )

            if rig_feature_set != "Lite":
                layout.prop(eyes, '["Eyelashes"]', text="Eyelash")

            layout.separator(type="LINE")

            layout.separator(type="LINE")
            panel_eyebrows(
                self,
                layout,
                pose,
                py_panel_helper,
                py_materials,
                collections,
                rig_feature_set,
            )
            layout.separator(type="LINE")
            panel_iris(
                layout,
                pose,
                py_panel_helper,
                py_materials,
                collections,
                rig_feature_set,
            )
            layout.separator(type="LINE")
            panel_sclera(layout, pose, py_panel_helper, py_materials, collections)

            layout.separator(type="LINE")
            panel_mouth(layout, pose, py_panel_helper, py_materials, collections)


def panel_eyebrows(
    cls, parent_ui, pose, python, materials, collections, rig_feature_set
):
    """Perform panel eyebrows."""
    props_eb = pose["Eyebrow_Properties"]

    panel = global_ui.sub_panel(
        parent_ui, python, prop="EyebrowPanel", label="Eyebrows"
    )
    if panel:
        panel.label(text="Eyebrows")

        col = panel.column(align=True)
        col.prop(props_eb, '["Depth"]')
        col.prop(props_eb, '["Thickness"]')
        col.prop(props_eb, '["Width"]')

        try:
            mat = materials.get("eye_brow").node_tree.nodes["Eyebrow_Shader"]
            node = mat.inputs
            ui.tables.eye_colors(
                parent_ui=panel,
                material=mat,
                grid=(
                    "L.Color In",
                    "R.Color In",
                    "L.Color Out",
                    "R.Color Out",
                    "Gradient",
                    "Split Color",
                ),
                grid_label=("", "", "", "", "Gradient", "Separate"),
            )

            col = panel.column(heading="Reflections")
            col.prop(node["IOR"], "default_value", text="IOR")
            col.prop(node["Metalic"], "default_value", text="Specular")
            col.prop(node["Specular"], "default_value", text="Roughness")

            col = panel.column(heading="Coat/Sheet")
            col.prop(node["Coat IOR"], "default_value", text="IOR")
            col.prop(node["Sheen Roughness"], "default_value", text="Roughness")

            col = panel.column(heading="Emission")
            row = col.row()
            row.prop(node[12], "default_value", text="Emission", toggle=True)
            row2 = row.row()
            row2.enabled == node[12].default_value
            row2.prop(node[13], "default_value", text="Strength")
        except:
            pass


def panel_iris(parent_ui, pose, python, materials, collections, rig_feature_set):
    """Perform panel iris."""
    eyes = pose["Eye_Properties"]
    panel = global_ui.sub_panel(parent_ui, python, prop="IrisPanel", label="Iris")
    if panel:
        panel.label(text="Settings", icon="PREFERENCES")
        col = panel.column()
        col.prop(eyes, '["Iris Inset"]')
        if rig_feature_set != "Lite":
            col.prop(eyes, '["Eyesparkle"]', toggle=True)

        panel.separator(type="LINE")

        try:
            col = panel.column()
            col.label(text="Colors", icon="COLOR")
            mat = materials.get("eye_iris").node_tree.nodes["Iris_Shader"]
            ui.tables.eye_colors(
                parent_ui=col,
                material=mat,
                grid=(
                    "Color1.L",
                    "Color1.R",
                    "Color2.L",
                    "Color2.R",
                    "Gradient",
                    "Heterochromia",
                ),
                grid_label=("", "", "", "", "Gradient", "Heterochromia"),
            )
            col = panel.column()
            col.label(text="Reflections", icon="SHADING_RENDERED")
            col.prop(mat.inputs[7], "default_value", text="IOR")
            col.prop(mat.inputs[19], "default_value", text="Metallic")
            col.prop(mat.inputs[20], "default_value", text="Specular")
            col.prop(mat.inputs[21], "default_value", text="Roughness")

            col = panel.column()
            col.label(text="Clearcoat", icon="SHADING_RENDERED")
            col.prop(mat.inputs[24], "default_value", text="Weight")
            col.prop(mat.inputs[25], "default_value", text="Roughness")
            col.prop(mat.inputs[26], "default_value", text="IOR")

            col = panel.column()

            col.prop(
                mat.inputs[31],
                "default_value",
                text="Emission",
                toggle=True,
                icon=(
                    "OUTLINER_OB_LIGHT"
                    if mat.inputs[31].default_value
                    else "OUTLINER_DATA_LIGHT"
                ),
            )
            if mat.inputs[31].default_value:
                col.prop(
                    mat.inputs[33],
                    "default_value",
                    text="Split",
                    toggle=True,
                    icon="UNLINKED" if mat.inputs[33].default_value else "LINKED",
                )

                if mat.inputs[33].default_value:
                    col = panel.box().column()
                    col.label(text="Emission Strength")
                    ui.tables.eye_colors(
                        parent_ui=col,
                        material=mat,
                        grid=(36, 38, 37, 39, 35, 34),
                        grid_label=("", "", "", "", "Gradient", "Heterochromia"),
                    )
                else:
                    col.prop(mat.inputs[36], "default_value", text="Strength")

            col.separator(type="LINE")

            col.prop(
                mat.inputs["Pupils"],
                "default_value",
                text="Pupuls",
                toggle=True,
                icon="HIDE_OFF" if mat.inputs["Pupils"].default_value else "HIDE_ON",
            )
            if mat.inputs["Pupils"].default_value:
                box = col.box()
                box.prop(mat.inputs[41], "default_value", text="Color")
                box.prop(mat.inputs[42], "default_value", text="Opacity")
                box.prop(mat.inputs[43], "default_value", text="Custom Texture")

                if mat.inputs[43].default_value:
                    pass
                    # Need Image Switcher setup here
                else:
                    col = box.column()
                    col.label(text="Size")
                    row = col.row(align=True)
                    row.prop(mat.inputs[45], "default_value", text="X")
                    row.prop(mat.inputs[46], "default_value", text="Y")
        except:
            pass


def panel_sclera(parent_ui, pose, python, materials, collections):
    """Perform panel sclera."""
    eyes = pose["Eye_Properties"]
    panel = global_ui.sub_panel(parent_ui, python, prop="ScleraPanel", label="Scleras")
    if panel:
        panel.label(text="Settings", icon="PREFERENCES")
        panel.prop(eyes, '["Sclera Depth"]', text="Depth")

        try:

            col = panel.column()
            col.label(text="Colors", icon="COLOR")
            mat = materials.get("eye_sclera").node_tree.nodes["Sclera_Shader"]
            ui.tables.eye_colors(
                parent_ui=col,
                material=mat,
                grid=(
                    "Color1.L",
                    "Color1.R",
                    "Color2.L",
                    "Color2.R",
                    "Gradient",
                    "Heterochromia",
                ),
                grid_label=("", "", "", "", "Gradient", "Heterochromia"),
            )

            col = panel.column()
            col.label(text="Reflections", icon="SHADING_RENDERED")
            col.prop(mat.inputs[7], "default_value", text="IOR")
            col.prop(mat.inputs[19], "default_value", text="Metallic")
            col.prop(mat.inputs[20], "default_value", text="Specular")
            col.prop(mat.inputs[21], "default_value", text="Roughness")

            col = panel.column()
            col.label(text="Clearcoat", icon="SHADING_RENDERED")
            col.prop(mat.inputs[24], "default_value", text="Weight")
            col.prop(mat.inputs[25], "default_value", text="Roughness")
            col.prop(mat.inputs[26], "default_value", text="IOR")

            col = panel.column(heading="Emissions")
            col.prop(
                mat.inputs[31],
                "default_value",
                text="Emission",
                toggle=True,
                icon=(
                    "OUTLINER_OB_LIGHT"
                    if mat.inputs[31].default_value
                    else "OUTLINER_DATA_LIGHT"
                ),
            )
            if mat.inputs[31].default_value:
                col.prop(mat.inputs[33], "default_value", text="Split", toggle=True)
                if mat.inputs[33].default_value:
                    col = panel.box().column()
                    col.label(text="Emission Strength")
                    ui.tables.eye_colors(
                        parent_ui=col,
                        material=mat,
                        grid=(36, 38, 37, 39, 35, 34),
                        grid_label=("", "", "", "", "Gradient", "Heterochromia"),
                    )
                else:
                    panel.prop(mat.inputs[36], "default_value", text="Strength")
        except:
            pass


def panel_mouth(parent_ui, pose, python, materials, collections):
    """Perform panel mouth."""
    props = pose["Mouth_Properties"]
    panel = global_ui.sub_panel(parent_ui, python, prop="MouthPanel", label="Mouth")
    if panel:
        panel.prop(props, '["Classic Mouth"]', text="Shallow Mouth", toggle=True)
        panel.prop(props, '["Square Mouth"]')

        try:
            mouth_inside = materials.get("mouth_inside").node_tree.nodes["Mouth_Inside"]
            teeth = materials.get("mouth_teeth").node_tree.nodes["Teeth_Shader"]

            panel.prop(
                mouth_inside.inputs["Base Color"],
                "default_value",
                text="Mouth Inside Color",
            )

            panel.prop(teeth.inputs["Base Color"], "default_value", text="Teeth Color")
            panel.prop(
                teeth.inputs["Emission"],
                "default_value",
                text="Emission Toggle",
                toggle=True,
            )
            if teeth.inputs["Emission"].default_value:
                box = panel.box()
                box.prop(teeth.inputs[31], "default_value", text="Emission Color")

                box.prop(teeth.inputs[32], "default_value", text="Emission Strength")
        except:
            pass


def register():
    """Register this module's Blender classes."""
    U.register_class(PT_Face)


def unregister():
    """Unregister this module's Blender classes."""
    U.unregister_class(PT_Face)
