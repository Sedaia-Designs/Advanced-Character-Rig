# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from .lib import SkinUtils


class DownloadSkin(T.Operator):
    bl_idname = Prefixer("download_skin").operator
    bl_label = "Download Skin"

    def execute(self, context):
        prefs = get_preferences()
        scene = context.scene
        skin_utils = SkinUtils(scene.skins_username)

        new_cache = skin_utils.write_new_cache()

        if new_cache == 'already_cached':
            self.report({'INFO'}, "Skin cache already up to date")
            
        elif new_cache == 'http_error':
            self.report({'ERROR'}, "Failed to download skin cache")
            return {'CANCELLED'}

        O.sedaia_rigs_ot.refresh_skin_list()
        return {'FINISHED'}


# Registering
def register():
    bpy.utils.register_class(DownloadSkin)


def unregister():
    bpy.utils.unregister_class(DownloadSkin)


if __name__ == "__main__":
    register()
