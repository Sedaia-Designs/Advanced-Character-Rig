import bpy
import bpy.types as T
import bpy.utils as U
from ...preferences import Prefixer
from ...operators.lib import blender_utils as utils
from .lib import (
    SACR7_UI2_Panel_Base,
    rig_ver,
    ui_ver,
    config_objs,
)

class SACR7_UI2_sui_quick_parent(SACR7_UI2_Panel_Base, T.Panel):
    bl_label = "Quick Parents"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_quick_parent").panel
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 3

    def draw(self, context):
        panel = self.layout
        rig = context.active_object
        rig_data = rig.data
        rig_bc = rig_data.collections_all

        t_row = panel.row()
        t_row.prop(rig_bc["Quick Parents"], "is_visible", text="QP Show Objects",
                   icon="HIDE_ON" if rig_bc["Quick Parents"].is_visible is False else "HIDE_OFF")

        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=True)
        p_col.prop(rig_bc["QP.Head"], "is_visible", text="Head",
                   icon="HIDE_ON" if rig_bc["QP.Head"].is_visible is False else "HIDE_OFF")

        panel.separator(type="SPACE")
        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=True)
        p_col.prop(rig_bc["QP.Torso"], "is_visible", text="Torso",
                   icon="HIDE_ON" if rig_bc["QP.Torso"].is_visible is False else "HIDE_OFF")
        d_row = p_col.row(align=True)
        d_row.enabled = rig_bc["QP.Torso"].is_visible
        d_row.prop(rig_bc["QP.Chest"], "is_visible", text="Chest",
                   icon="HIDE_ON" if rig_bc["QP.Chest"].is_visible is False else "HIDE_OFF")
        d_row.prop(rig_bc["QP.Hip"], "is_visible", text="Hips",
                   icon="HIDE_ON" if rig_bc["QP.Hip"].is_visible is False else "HIDE_OFF")
        d_row.prop(rig_bc["QP.Pelvis"], "is_visible", text="Root",
                   icon="HIDE_ON" if rig_bc["QP.Pelvis"].is_visible is False else "HIDE_OFF")

        panel.separator(type="SPACE")
        p_row = panel.row(align=True)
        p_row.enabled = rig_bc["Quick Parents"].is_visible
        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm L"], "is_visible", text="Left Arm",
                   icon="HIDE_ON" if rig_bc["QP.Arm L"].is_visible is False else "HIDE_OFF")
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm L"].is_visible
        d_col.prop(rig_bc["QP.Shoulder L"], "is_visible", text="Shoulder",
                   icon="HIDE_ON" if rig_bc["QP.Shoulder L"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Forearm L"], "is_visible", text="Forearm",
                   icon="HIDE_ON" if rig_bc["QP.Forearm L"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Hand L"], "is_visible", text="Hand",
                   icon="HIDE_ON" if rig_bc["QP.Hand L"].is_visible is False else "HIDE_OFF")

        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm R"], "is_visible", text="Right Arm",
                   icon="HIDE_ON" if rig_bc["QP.Arm R"].is_visible is False else "HIDE_OFF")
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm R"].is_visible
        d_col.prop(rig_bc["QP.Shoulder R"], "is_visible", text="Shoulder",
                   icon="HIDE_ON" if rig_bc["QP.Shoulder R"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Forearm R"], "is_visible", text="Forearm",
                   icon="HIDE_ON" if rig_bc["QP.Forearm R"].is_visible is False else "HIDE_OFF")
        d_col.prop(rig_bc["QP.Hand R"], "is_visible", text="Hand",
                   icon="HIDE_ON" if rig_bc["QP.Hand R"].is_visible is False else "HIDE_OFF")


classes = [
    SACR7_UI2_sui_quick_parent,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
