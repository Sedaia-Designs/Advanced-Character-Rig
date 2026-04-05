# Imports
from urllib import request

import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer

class DownloadManifest(T.Operator):
    bl_idname = Prefixer("download_manifest").operator
    bl_label = "Download Manifest"
    bl_description = "Download the manifest from https://sakura-sedaia.com/"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.report({'INFO'}, "Downloading manifest...")
        
        wm = context.window_manager
        wm.progress_begin(0, 100)

        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                wm.progress_update(min(max(0, percent), 100))

        try:
            request.urlretrieve(
                "https://sakura-sedaia.com/docs/sacr-index.json", 
                get_preferences().addon_directory + "/Manifest.json",
                reporthook=reporthook
            )
            import time
            get_preferences().last_manifest_refresh = time.time()
            self.report({'INFO'}, "Manifest downloaded successfully")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download manifest: {e}")
            wm.progress_end()
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
