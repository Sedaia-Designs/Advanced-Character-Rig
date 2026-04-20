# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
import json
from pathlib import Path

from ..preferences import Prefixer, get_preferences

class OpenInViewer(T.Operator):
    bl_idname = Prefixer("open_in_viewer").operator
    bl_label = "Preview Skin"
    bl_description = "Open the selected skin texture in the system's default image viewer"
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(name="Player Name")

    def execute(self, context):
        scene = context.scene
        skin_props = scene.sacr_skins_collection
        
        # Find the selected player in the skin list
        selected_player = next((item for item in skin_props.sacr_skins_collection if item.name == self.name), None)
        
        if not selected_player:
            self.report({'ERROR'}, f"Player '{self.name}' not found in the skin list.")
            return {'CANCELLED'}

        from .lib import SkinUtils
        skin_utils = SkinUtils(self.name)
        
        try:
            skin_index = int(selected_player.skin_texture_enum)
        except ValueError:
            self.report({'ERROR'}, "Invalid skin selection.")
            return {'CANCELLED'}

        skin_path = skin_utils.get_skin_path(skin_index)
        
        if not skin_path or not skin_path.exists():
            self.report({'ERROR'}, f"Skin texture file not found: {skin_path}")
            return {'CANCELLED'}

        # Open the file in the system default viewer
        bpy.ops.wm.path_open(filepath=str(skin_path))
        self.report({'INFO'}, f"Opened skin: {skin_path.name}")

        return {'FINISHED'}

# Registering
def register():
    U.register_class(OpenInViewer)


def unregister():
    U.unregister_class(OpenInViewer)


if __name__ == "__main__":
    register()
