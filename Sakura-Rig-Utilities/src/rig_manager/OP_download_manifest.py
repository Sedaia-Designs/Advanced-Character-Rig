# Imports
from urllib import request

import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from ..operators.lib.blender_utils import allow_online

class DownloadManifest(T.Operator):
    bl_idname = Prefixer("download_manifest").operator
    bl_label = "Download Manifest"
    bl_description = "Download the manifest from https://sakura-sedaia.com/"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not allow_online():
            self.report({'WARNING'}, "Online functionality is disabled in Blender settings.")
            return {'CANCELLED'}

        self.report({'INFO'}, "Downloading manifest...")
        
        wm = context.window_manager
        wm.progress_begin(0, 100)

        def progress_callback(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                wm.progress_update(min(max(0, percent), 100))

        try:
            from .lib import SacrDownloader
            success, message = SacrDownloader.download_manifest(progress_callback=progress_callback)
            
            if success:
                self.report({'INFO'}, message)
            else:
                self.report({'ERROR'}, f"Failed to download manifest: {message}")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unexpected error during manifest download: {e}")
            return {'CANCELLED'}
        finally:
            wm.progress_end()
            
        return {'FINISHED'}

# Registering
def register():
    U.register_class(DownloadManifest)


def unregister():
    U.unregister_class(DownloadManifest)


if __name__ == "__main__":
    register()
