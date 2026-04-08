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

class SEDAIA_PT_sacr_7_ui_1_eyes(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "Eyes Settings"
    bl_parent_id = Prefixer("sacr_7_ui_1_face_main").panel
    bl_idname = Prefixer("sacr_7_ui_1_eyes").panel
    bl_order = 1

    def draw(self, context):
        # Variables and Data
        obj = context.active_object
        armature = obj.data
        bone = obj.pose.bones

        eyes = bone["Eye_Properties"]

        lite = armature.get("lite", False)

        try:
            if eyes["Eyesparkle"] == 0 or 1:
                sparkle = True
        except (AttributeError, TypeError, KeyError):
            sparkle = False

        lashTog = eyes['Eyelashes'] > 0

        # Face Material Objs
        rig_child = obj.children_recursive

        if obj.data.get(id_prop) == id_str[0]:
            matObj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)
            lashMat = matObj.material_slots[7].material.node_tree.nodes['Group']
            sparkleMat = matObj.material_slots[5].material.node_tree.nodes['Emission']

        # UI
        layout = self.layout
        row = layout.row()
        col = row.column(align=True)
        col.prop(eyes, '["Iris Inset"]', slider=True)
        col.prop(eyes, '["Sclera Depth"]', slider=True)

        if not lite:
            row = col.row(align=True)
            row.prop(eyes, '["Eyelashes"]', text="Lash Style")

            if obj.data.get(id_prop) == id_str[0]:
                rowTog = row.row(align=True)
                rowTog.enabled = lashTog
                rowTog.prop(lashMat.inputs['Base Color'],
                            'default_value', text="")

            if sparkle:
                row = col.row(align=True)
                row.prop(eyes, '["Eyesparkle"]', toggle=True, text="Sparkle")

                if obj.data.get(id_prop) == id_str[0]:
                    rowTog = row.row(align=True)
                    rowTog.enabled = eyes['Eyesparkle']
                    rowTog.prop(sparkleMat.inputs[0], 'default_value', text="")

        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="More Controls")
        row = layout.row(align=True)
        row.prop(eyes, '["Extended Controls"]',
                 index=0, text="Left", slider=False)
        row.prop(eyes, '["Extended Controls"]',
                 index=1, text="Right", slider=False)


classes = [
    SEDAIA_PT_sacr_7_ui_1_eyes,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
