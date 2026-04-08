import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ...operators.lib import blender_utils as utils
from ...preferences import Prefixer
from .lib import (
    SACR8_UI1_Panel_Base,
    rig_ver,
    ui_ver,
    mat_obj_name,
    prop_bones,
)

class SEDAIA_PT_SACR8_ui_global(SACR8_UI1_Panel_Base, T.Panel):
    bl_label = "SACR Properties"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_order = 0

    def draw(self, context):
        # Rig Data
        rig = context.active_object
        rig_data = rig.data
        rig_bones = rig.pose.bones
        # scene = context.scene # Unused in original draw

        # set Child Object Indices
        mat_obj = None
        for l in rig.children:
            # Find Material Object
            objName = l.name.split(".")[0]
            if objName == mat_obj_name:
                mat_obj = l
                break

        if not mat_obj:
             return

        skin = mat_obj.material_slots[0].material.node_tree
        skinTex = skin.nodes["Skin Texture"].image
        mainProp = rig_bones[prop_bones[0]]
        panel = self.layout

        p_row = panel.row()
        p_row.label(text="Utilities")

        p_row = panel.row()
        p_row.label(text="Skin Texture")
        i_row = panel.row(align=True)
        
        # Using standardized operators if possible, otherwise use the ones from Prefixer
        i_row.operator(Prefixer("image_pack").operator, icon="PACKAGE" if utils.is_packed(
            skinTex) else "UGLYPACKAGE", text="").path = skinTex.name
            
        i_row = i_row.row(align=True)
        i_row.enabled = not utils.is_packed(skinTex)
        i_row.prop(skinTex, "filepath", text="")
        i_row.operator(Prefixer("image_reload").operator, icon="FILE_REFRESH",
                       text="").path = skinTex.name

        p_row = panel.row()

        p_col = p_row.column_flow(columns=2, align=True)
        p_col.prop(rig.pose, "use_mirror_x", toggle=True)
        p_col.prop(mainProp, '["Anti-Lag"]', toggle=True)

        panel.separator(type="LINE")

class SEDAIA_PT_SACR8_sui_QuickParentCTRL(SACR8_UI1_Panel_Base, T.Panel):
    bl_parent_id = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_global").panel
    bl_label = "Quick Parent Objects"
    bl_idname = Prefixer(f"sacr_{rig_ver}_ui_{ui_ver}_quick_parent").panel
    bl_order = 5

    def draw(self, context):
        panel = self.layout

        rig = context.active_object
        rig_data = rig.data

        rig_bc = rig_data.collections_all

        t_row = panel.row()
        t_row.prop(rig_bc["Quick Parenting Objects"],
                   "is_visible", text="QP Show Objects", toggle=False)

        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parenting Objects"].is_visible
        p_col = p_row.column(align=True)
        c_row = p_col.row()
        c_row.prop(rig_bc["QP.Head"], "is_visible", text="Head", toggle=True)

        panel.separator(type="SPACE")

        p_row = panel.row()
        p_row.enabled = rig_bc["Quick Parenting Objects"].is_visible
        p_col = p_row.column(align=True)
        c_row = p_col.row()
        c_row.prop(rig_bc["QP.Torso"], "is_visible", text="Torso", toggle=True)
        d_row = p_col.row(align=True)
        d_row.enabled = rig_bc["QP.Torso"].is_visible
        d_row.prop(rig_bc["QP.Chest"], "is_visible", text="Chest", toggle=True)
        d_row.prop(rig_bc["QP.Hip"], "is_visible", text="Hips", toggle=True)
        d_row.prop(rig_bc["QP.Pelvis"], "is_visible", text="Root", toggle=True)

        panel.separator(type="SPACE")

        p_row = panel.row(align=True)
        p_row.enabled = rig_bc["Quick Parenting Objects"].is_visible
        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm L"], "is_visible",
                   text="Left Arm", toggle=True)
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm L"].is_visible
        d_col.prop(rig_bc["QP.Shoulder L"], "is_visible",
                   text="Shoulder", toggle=True)
        d_col.prop(rig_bc["QP.Forearm L"], "is_visible",
                   text="Forearm", toggle=True)
        d_col.prop(rig_bc["QP.Hand L"], "is_visible", text="Hand", toggle=True)

        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Arm R"], "is_visible",
                   text="Right Arm", toggle=True)
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Arm R"].is_visible
        d_col.prop(rig_bc["QP.Shoulder R"], "is_visible",
                   text="Shoulder", toggle=True)
        d_col.prop(rig_bc["QP.Forearm R"], "is_visible",
                   text="Forearm", toggle=True)
        d_col.prop(rig_bc["QP.Hand R"], "is_visible", text="Hand", toggle=True)

        panel.separator(type="SPACE")

        p_row = panel.row(align=True)
        p_row.enabled = rig_bc["Quick Parenting Objects"].is_visible
        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Leg L"], "is_visible",
                   text="Left Leg", toggle=True)
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Leg L"].is_visible
        d_col.prop(rig_bc["QP.Thigh L"], "is_visible",
                   text="Thigh", toggle=True)
        d_col.prop(rig_bc["QP.Knee L"], "is_visible", text="Knee", toggle=True)

        p_col = p_row.column(align=False)
        p_col.prop(rig_bc["QP.Leg R"], "is_visible",
                   text="Right Leg", toggle=True)
        d_col = p_col.column(align=True)
        d_col.enabled = rig_bc["QP.Leg R"].is_visible
        d_col.prop(rig_bc["QP.Thigh R"], "is_visible",
                   text="Thigh", toggle=True)
        d_col.prop(rig_bc["QP.Knee R"], "is_visible", text="Knee", toggle=True)

classes = [
    SEDAIA_PT_SACR8_ui_global,
    SEDAIA_PT_SACR8_sui_QuickParentCTRL,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
