# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from .lib import SkinUtils

class RefreshSkinList(T.Operator):
    bl_idname = Prefixer("refresh_skin_list").operator
    bl_label = "Refresh Skin List"
    bl_description = "Refresh the skin list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            prefs = get_preferences()
            addon_dir = prefs.addon_directory

            skins_data = SkinUtils.get_all_skins(addon_dir)

            scene = context.scene
            skin_props = scene.sacr_skins_collection

            # Clear existing sacr_skins_collection
            skin_props.sacr_skins_collection.clear()

            for skin in skins_data:
                item = skin_props.sacr_skins_collection.add()
                item.name = skin["name"]
                item.uuid = skin["uuid"]
                item.json_path = skin["json_path"]
                
            self.report({'INFO'}, f"Refreshed skin list: {len(skins_data)} skins found.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh skin list: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Registering
def register():
    U.register_class(RefreshSkinList)


def unregister():
    U.unregister_class(RefreshSkinList)


if __name__ == "__main__":
    register()
