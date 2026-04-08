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

class SACR7_UI2_sui_armor(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Armor"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_armor").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 4

    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        return context.active_object.data.get('lite', False) is False

    def draw(self, context):
        rig = context.active_object
        rig_bones = rig.pose.bones
        rig_child = rig.children_recursive
        mat_obj = utils.lookup_name(bl_list=rig_child, query=ConfigObjs.materials)
        mainProp = rig_bones[ConfigObjs.main]

        panel = self.layout
        col = panel.column(align=True)

        armor_parts = [
            ("Helmet", 8),
            ("Chestplate", 9),
            ("Leggings", 10),
            ("Boots", 11)
        ]

        for i, (name, slot_idx) in enumerate(armor_parts):
            row = col.row()
            row.prop(mainProp, '["Armor Toggle"]', index=i, text=name,
                     icon="HIDE_ON" if mainProp["Armor Toggle"][i] is False else "HIDE_OFF")
            
            img = mat_obj.material_slots[slot_idx].material.node_tree.nodes["Armor Texture"].image
            row = col.row(align=True)
            row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(img) else "UGLYPACKAGE", text="").path = img.name
            row_f = row.row(align=True)
            row_f.enabled = not utils.is_packed(img)
            row_f.prop(img, "filepath", text="")
            row.operator(Prefixer("image_reload").operator, icon="FILE_REFRESH", text="").path = img.name
            
            if i < len(armor_parts) - 1:
                col.separator(type='SPACE')
                col.separator(type='LINE')
                col.separator(type='SPACE')


classes = [
    SACR7_UI2_sui_armor,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
