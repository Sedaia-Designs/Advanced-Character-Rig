"""The extension's user preferences."""

import bpy.props as P
import bpy.types as T

from ..operators.constants import OperatorID
from .access import storage_dir
from .constants import ADDON_PACKAGE


class PREFS_user_preferences(T.AddonPreferences):
    bl_idname = ADDON_PACKAGE

    prompt_to_refresh_player_data: P.BoolProperty(
        name="Prompt to Regen Player Data",
        default=True,
    )

    def draw(self, context):
        # Imported here, not at module level: importing `features` while this
        # package loads would run the Skin Manager operators, which import
        # `preferences.access` from this half-loaded package.
        from ..features.skin_manager.operators.constants import OperatorID as SkinOperatorID

        layout = self.layout
        layout.operator(OperatorID.FILE_OPEN, icon="FILEBROWSER").path = storage_dir()

        box = layout.box()
        box.label(text="Skin Manager")
        col = box.column()
        col.prop(self, "prompt_to_refresh_player_data", toggle=True)
        col.operator(SkinOperatorID.IMPORT_LEGACY, text="Import Legacy Player Data", icon="IMPORT")


classes = (
    PREFS_user_preferences,
)
