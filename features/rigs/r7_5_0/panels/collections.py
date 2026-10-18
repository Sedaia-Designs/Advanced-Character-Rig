from ..ui import types
from ..ui import ID, RIG_ID_GROUP, ui as global_ui
import bpy.utils as U


class PT_Collections(types.SACR_UI750_Panel):
    bl_label = "Control Groups"
    bl_idname = ID("collections").panel_for(RIG_ID_GROUP)
    bl_order = 2

    def draw(self, context):

        """Draw this UI element for the current Blender context."""
        def collection(parent_ui, group: str, name: str, toggle=True):
            """Perform collection."""
            parent_ui.prop(collections[group], "is_visible", text=name, toggle=toggle)

        def is_on(collection_name: str):
            """Return whether on."""
            return collections[collection_name].is_visible

        def group_header(parent_ui, group: str, label: str):
            """Perform group header."""
            header = parent_ui.row()
            header.prop(
                collections[group],
                "is_visible",
                text="",
                icon="CHECKBOX_HLT" if is_on(group) else "CHECKBOX_DEHLT",
            )
            header.label(text=label)

        obj = context.active_object
        pose = obj.pose.bones
        collections = obj.data.collections_all
        python = pose["PythonConfig.Objects"]
        py_panel_helper = pose["PythonConfig.PanelHelper"]

        layout = self.layout

        panel = global_ui.sub_panel(layout, py_panel_helper, "FaceBoneColPanel", "Face")
        if panel:
            box = panel.box()
            col = box.column()
            group_header(col, "Eyebrows", "Eyebrow Controls")
            row = col.row(align=True)
            row.enabled = collections["Eyebrows"].is_visible
            col2 = row.column(align=True, heading="Left")
            c_row = col2.row(align=True)
            c_row.prop(
                collections["Eyebrow_Left_Simplified"],
                "is_visible",
                text="Simple",
                toggle=True,
            )

            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eyebrow_Left_Simplified")
            c_row2.prop(
                collections["Eyebrow_Left_Advanced"],
                "is_visible",
                text="Advanced",
                toggle=True,
            )

            col2 = row.column(align=True, heading="Right")
            c_row = col2.row(align=True)
            c_row.prop(
                collections["Eyebrow_Right_Simplified"],
                "is_visible",
                text="Simple",
                toggle=True,
            )

            c_row2 = col2.row(align=True)
            c_row2.enabled = collections["Eyebrow_Right_Simplified"].is_visible
            c_row2.prop(
                collections["Eyebrow_Right_Advanced"],
                "is_visible",
                text="Advanced",
                toggle=True,
            )

            panel.separator(type="LINE")

            box = panel.box()
            col = box.column()
            group_header(col, "Eyes", "Eye Controls")
            row = col.row(align=True)
            row.enabled = is_on("Eyes")

            col2 = row.column(align=True, heading="Left")
            c_row = col2.row(align=True)
            collection(c_row, "Eye_Left_Simplified", "Simple")

            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eye_Left_Simplified")
            collection(c_row2, "Eye_Left_Advanced", "Advanced")

            col2 = row.column(align=True, heading="Right")
            c_row = col2.row(align=True)
            collection(c_row, "Eye_Right_Simplified", "Simple")

            c_row2 = col2.row(align=True)
            c_row2.enabled = is_on("Eye_Right_Simplified")
            collection(c_row2, "Eye_Right_Advanced", "Advanced")

            panel.separator(type="LINE")

            box = panel.box()
            col = box.column()
            group_header(col, "Mouth", "Mouth Controls")
            row = col.row(align=True)

            row = col.row(align=True)
            row.enabled = collections["Mouth"].is_visible
            collection(row, "Mouth_Advanced", "Extra")

        layout.separator(type="LINE")
        panel = global_ui.sub_panel(layout, py_panel_helper, "BodyBoneColPanel", "Body")
        if panel:
            col = panel.column(heading="Upper Body")
            row = col.row()
            collection(row, "Torso", "Torso")

            row_u = col.row(align=True)
            collection(row_u, "Arm_Left", "Left Arm")
            collection(row_u, "Arm_Right", "Right Arm")

            col = panel.column(heading="Lower Body")
            row_l = col.row()
            collection(row_l, "Leg_Left", "Left Leg")
            collection(row_l, "Leg_Right", "Right Leg")


def register():
    """Register this module's Blender classes."""
    U.register_class(PT_Collections)


def unregister():
    """Unregister this module's Blender classes."""
    U.unregister_class(PT_Collections)
