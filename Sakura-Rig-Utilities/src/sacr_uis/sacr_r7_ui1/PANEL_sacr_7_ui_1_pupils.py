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

class SEDAIA_PT_sacr_7_ui_1_pupils(SACR7_UI1_Face_Panel_Base, T.Panel):
    bl_label = "Pupil Material"
    bl_parent_id = Prefixer("sacr_7_ui_1_eyes").panel
    bl_idname = Prefixer("sacr_7_ui_1_pupils").panel
    bl_order = 1

    def draw(self, context):
        obj = context.active_object
        rig_child = obj.children_recursive

        if obj.data.get(id_prop) == id_str[0]:
            matObj = utils.lookup_name(bl_list=rig_child, query=mesh_mat_obj)

        irisMat = matObj.material_slots[1].material.node_tree.nodes['Group.001']

        # UI
        layout = self.layout

        row = layout.row()
        row.label(text="Colors", icon="SHADING_RENDERED")

        row = layout.row(align=True)
        row.prop(irisMat.inputs['Pupil Toggle'],
                 'default_value', text="Opacity", slider=True)
        row.prop(irisMat.inputs['Color'], 'default_value', text='')

        row = layout.row(align=True)
        col = row.column(align=True)
        col.label(text="Pupil Scale")
        row = col.row(align=True)
        row.prop(irisMat.inputs['Scale1'],
                 'default_value', text='X', slider=True)
        row.prop(irisMat.inputs['Scale2'],
                 'default_value', text='Y', slider=True)

        layout.separator(type="LINE")
        row = layout.row(align=True)
        row.label(text="Reflections", icon="MATERIAL_DATA")

        row = layout.row(align=True)
        irisCol = row.column(align=True)
        irisCol.prop(irisMat.inputs[27], 'default_value', text="Metalic")
        irisCol.prop(irisMat.inputs[28], 'default_value', text="Specular")
        irisCol.prop(irisMat.inputs[29], 'default_value', text="Roughness")

        layout.separator(type="LINE")

        row = layout.row()
        row.label(text="Emission", icon="OUTLINER_OB_LIGHT")
        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.prop(irisMat.inputs['Emission Mask'],
                 'default_value', text="Toggle")
        row1 = row.row(align=True)
        row1.enabled = irisMat.inputs['Emission Mask'].default_value > 0
        row1.prop(irisMat.inputs['Strength'], 'default_value', text="Strength")
        row = col.row(align=True)
        row.enabled = irisMat.inputs['Emission Mask'].default_value > 0
        row.prop(irisMat.inputs['Emit_Color'], 'default_value', text="")


classes = [
    SEDAIA_PT_sacr_7_ui_1_pupils,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
