import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Face_Panel_Base,
    rig_ver,
    ui_ver,
    ConfigObjs,
)

class SACR7_UI2_sui_mouth(SACR7_UI2_Face_Panel_Base, T.Panel):
    bl_label = "Mouth"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_mouth").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_face").panel
    bl_order = 2

    def draw(self, context):
        rig = context.active_object
        rig_data = rig.data
        rig_bones = rig.pose.bones
        rig_bc = rig_data.collections_all
        props = rig_bones[ConfigObjs.mouth]
        rig_child = rig.children_recursive

        mat_obj = utils.lookup_name(bl_list=rig_child, query=ConfigObjs.materials)
        mouth_back = mat_obj.material_slots[3].material.node_tree.nodes['Material']
        teeth = mat_obj.material_slots[4].material.node_tree.nodes['Material']

        panel = self.layout
        row = panel.row()
        row.label(text="Controller Toggle")
        row = panel.row()
        col = row.column()

        row = col.row(align=True)
        row.prop(rig_bc["Mouth"], 'is_visible', text="Basic",
                 icon="HIDE_ON" if rig_bc["Mouth"].is_visible is False else "HIDE_OFF")
        row_e = row.row(align=True)
        row_e.enabled = rig_bc['Mouth'].is_visible
        row_e.prop(rig_bc["Mouth_Advanced"], 'is_visible', text="Advanced",
                   icon="HIDE_ON" if rig_bc["Mouth_Advanced"].is_visible is False else "HIDE_OFF")

        row = panel.row()
        row.label(text="Options", icon="PROPERTIES")
        row = panel.row()
        col = row.column(align=True)
        col.prop(props, '["Square Mouth"]', slider=True, text="Square")
        crow = col.row(align=True)
        crow.prop(props, '["Classic Mouth"]', text="Shallow Mouth",
                  icon="CHECKBOX_HLT" if props.get('Classic Mouth', False) is True else "CHECKBOX_DEHLT")
        crow.prop(rig_bc['Molar Controls'], "is_visible", text="Molar Controls",
                  icon="HIDE_OFF" if rig_bc['Molar Controls'].is_visible is True else "HIDE_ON")

        panel.separator(type="LINE")
        row = panel.row()
        row.label(text="Colors", icon="MOD_COLOR_BALANCE")
        row = panel.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.label(text="Inside")
        row.label(text="Teeth")
        row = col.row(align=True)
        row.prop(mouth_back.inputs['Base Color'], "default_value", text="")
        row.prop(teeth.inputs['Base Color'], "default_value", text="")


classes = [
    SACR7_UI2_sui_mouth,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
