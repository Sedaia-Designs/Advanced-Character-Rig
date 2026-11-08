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
        layout = self.layout
        layout.operator(OperatorID.FILE_OPEN, icon="FILEBROWSER").path = storage_dir()

        col = layout.row().column()
        col.prop(self, "prompt_to_refresh_player_data", toggle=True)


classes = (
    PREFS_user_preferences,
)
