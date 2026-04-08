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

class SEDAIA_PT_sacr_7_ui_1_mouth(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "Mouth Settings"
    bl_parent_id = Prefixer("sacr_7_ui_1_face_main").panel
    bl_idname = Prefixer("sacr_7_ui_1_mouth").panel
    bl_order = 2

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        bone = obj.pose.bones
        mouth = bone["Mouth_Properties"]
        rig_child = obj.children_recursive

        if obj.data.get(id_prop) == id_str[0]:
            matObj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)
            backMat = matObj.material_slots[3].material.node_tree.nodes["Group.001"]
            teethMat = matObj.material_slots[4].material.node_tree.nodes["Group"]

        # UI
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        col.prop(mouth, '["Square Mouth"]', slider=True, text="Square")
        col.prop(mouth, '["Extended Controls"]', text="Extra Controls")

        if obj.data.get(id_prop) == id_str[0]:
            col.prop(backMat.inputs['Base Color'],
                     "default_value", text="Inside Color")
            col.prop(teethMat.inputs['Base Color'],
                     "default_value", text="Teeth Color")

        classic_molar = False
        try:
            mouth["Molar Height (R -> L)"]
        except (AttributeError, KeyError, TypeError):
            classic_molar = True

        if classic_molar:
            col.prop(
                mouth, '["Fangs Controller"]', toggle=True, text="Molar/Fang Controls"
            )
        else:
            col.separator()
            row = col.row()
            row.label(text="Molar Settings", icon="PROPERTIES")
            row = col.row()
            col = row.column(align=True)
            col.label(text="Left Height")

            top = "T"
            bottom = "B"

            col.prop(mouth, '["Molar Height (R -> L)"]',
                     index=3, slider=True, text=top)
            col.prop(
                mouth, '["Molar Height (R -> L)"]', index=2, slider=True, text=bottom
            )

            col = row.column(align=True)
            col.label(text="Right Height")
            col.prop(mouth, '["Molar Height (R -> L)"]',
                     index=0, slider=True, text=top)
            col.prop(
                mouth, '["Molar Height (R -> L)"]', index=1, slider=True, text=bottom
            )

            row = layout.row()
            col = row.column(align=True)
            col.label(text="Left Width")
            col.prop(mouth, '["Molar Width (R -> L)"]',
                     index=3, slider=True, text=top)
            col.prop(
                mouth, '["Molar Width (R -> L)"]', index=2, slider=True, text=bottom
            )

            col = row.column(align=True)
            col.label(text="Right Width")
            col.prop(mouth, '["Molar Width (R -> L)"]',
                     index=0, slider=True, text=top)
            col.prop(
                mouth, '["Molar Width (R -> L)"]', index=1, slider=True, text=bottom
            )


classes = [
    SEDAIA_PT_sacr_7_ui_1_mouth,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
