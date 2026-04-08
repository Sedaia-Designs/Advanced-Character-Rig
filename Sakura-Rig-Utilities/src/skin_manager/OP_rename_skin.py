# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import Prefixer
from .lib import SkinUtils

class RenameSkin(T.Operator):
    bl_idname = Prefixer("rename_skin").operator
    bl_label = "Rename Skin"
    bl_description = "Rename the selected skin texture"
    bl_options = {'REGISTER', 'UNDO'}

    new_name: P.StringProperty(name="New Name")

    def execute(self, context):
        scene = context.scene
        skin_props = scene.skins
        if not skin_props.skins:
            return {'CANCELLED'}

        selected_skin = skin_props.skins[skin_props.selected_skin]
        skin_index = int(selected_skin.skin_texture_enum)
        
        skin_utils = SkinUtils(selected_skin.name)
        result = skin_utils.rename_skin(skin_index, self.new_name)

        if result == 'complete':
            self.report({'INFO'}, f"Renamed skin to {self.new_name}")
            # We don't need to refresh the whole list, but we might need to force the enum to update
            # Actually, the enum items function will be called again next time it's drawn
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to rename skin")
            return {'CANCELLED'}

    def invoke(self, context, event):
        scene = context.scene
        skin_props = scene.skins
        if not skin_props.skins:
            return {'CANCELLED'}
            
        selected_skin = skin_props.skins[skin_props.selected_skin]
        
        # Pre-fill with current name if possible
        import json
        import os
        if selected_skin.json_path and os.path.exists(selected_skin.json_path):
            try:
                with open(selected_skin.json_path, 'r') as f:
                    data = json.load(f)
                    skin_index = int(selected_skin.skin_texture_enum)
                    skins = data.get("SKINS", [])
                    if 0 <= skin_index < len(skins):
                        self.new_name = skins[skin_index].get("name", f"Skin {skin_index}")
            except:
                pass

        return context.window_manager.invoke_props_dialog(self)

# Registering
def register():
    U.register_class(RenameSkin)

def unregister():
    U.unregister_class(RenameSkin)

if __name__ == "__main__":
    register()
