"""Viewport panel for downloading and applying Minecraft player skins."""

from bpy.types import Panel

from ... import prefs
from ..rigs.shared import OPS as UTILITY_OPS
from .constants import OPS, PANEL_ID
from .context import has_skin_metadata, skin_metadata


class SEDAIA_SKIN_PT:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Download Skins"


class SEDAIA_SKIN_PT_ui_skinUtility(SEDAIA_SKIN_PT, Panel):
    bl_label = "Skin Utility"
    bl_idname = PANEL_ID
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return has_skin_metadata(context)

    def draw(self, context):
        metadata = skin_metadata(context)
        layout = self.layout
        layout.label(text="Minecraft Username")
        column = layout.column(align=True)
        column.prop(metadata, '["Username"]', text="")
        row = column.row(align=True)
        row.operator(OPS["router"], icon="URL", text="Change Skin")
        row.operator(UTILITY_OPS["file_open"], icon="FILEBROWSER", text="Player Data").path = prefs.config["player_default_dir"]
        layout.separator(type="LINE")
        layout.label(text="Options")
        column = layout.column()
        column.prop(metadata, '["SyncArms"]', text="Sync Arm Type")
        if metadata.get("SyncCape", None) is not None:
            column.prop(metadata, '["SyncCape"]', text="Sync Cape Status")
        column.prop(metadata, '["SyncName"]', text="Set Rig Name to Username")


classes = (SEDAIA_SKIN_PT_ui_skinUtility,)
