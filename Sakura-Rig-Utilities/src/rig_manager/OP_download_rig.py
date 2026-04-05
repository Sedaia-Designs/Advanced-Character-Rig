# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
import os

from ..preferences import get_preferences, Prefixer
from .lib import SacrDownloader

class DownloadRig(T.Operator):
    bl_idname = Prefixer("download_rig").operator
    bl_label = "Download Rig"
    bl_description = "Download a rig from https://sakura-sedaia.com/"
    bl_options = {'REGISTER', 'UNDO'}

    version: P.StringProperty(
        name="Version",
        default="7.4.1",
        description="The version of the rig to download"
    )

    def execute(self, context):
        prefs = get_preferences()
        branch_id = prefs.sacr_branch
        self.report({'INFO'}, f"Downloading rig (Version: {self.version}, Branch: {'Stable' if branch_id == '0' else 'Dev'})...")

        wm = context.window_manager
        wm.progress_begin(0, 100)

        def progress_callback(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                wm.progress_update(min(max(0, percent), 100))

        try:
            downloader = SacrDownloader(branch_id)
            dest = downloader.download_version(self.version, progress_callback=progress_callback)
            
            self.report({'INFO'}, f"Rig downloaded successfully to {dest}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to download rig: {e}")
            return {'CANCELLED'}
        finally:
            wm.progress_end()

        return {'FINISHED'}

class DeleteRig(T.Operator):
    bl_idname = Prefixer("delete_rig").operator
    bl_label = "Delete Rig"
    bl_description = "Delete the rig from the addon directory"
    bl_options = {'REGISTER', 'UNDO'}

    version: P.StringProperty(
        name="Version",
        default="7.4.1",
        description="The version of the rig to delete"
    )

    def execute(self, context):
        try:
            SacrDownloader.delete_version(self.version)
            self.report({'INFO'}, f"Rig version {self.version} deleted successfully.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete rig: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

classes = [
    DownloadRig,
    DeleteRig
]

# Registering
def register():
    for cls in classes:
        U.register_class(cls)


def unregister():
    for cls in classes:
        U.unregister_class(cls)


if __name__ == "__main__":
    register()
