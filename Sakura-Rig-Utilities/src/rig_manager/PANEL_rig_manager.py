# Imports
import bpy
import bpy.types as T

from ..preferences import Prefixer, get_preferences
import os

class RigManagerPanel(T.Panel):
    bl_label = "SACR Rig Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SACR Utils"
    bl_order = 0
    bl_idname = Prefixer("rig_manager_ui").panel

    def draw_header(self, context):
        self.layout.label(text="", icon="ARMATURE_DATA")

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()
        scene = context.scene

        row = layout.row()
        column = row.column(align=True)
        rig_props = scene.rigs
        column.template_list(Prefixer("rig_list").list, "", rig_props, "rigs", rig_props, "selected_rig")

        row = column.row(align=True)
        row.operator(Prefixer("refresh_rig_list").operator, icon="FILE_REFRESH", text="")
        row.operator(Prefixer("append_rig").operator, icon="APPEND_BLEND")

        row = layout.row(align=True)
        row.operator(Prefixer("open_addon_directory").operator, icon="FILE_FOLDER")

        layout.separator()

        download_panel = layout.panel(idname=Prefixer("download_panel").panel, default_closed=True)

        header = download_panel[0]
        header.label(text="Downloader", icon="IMPORT")

        content = download_panel[1]
        if content is not None:
            col = layout.box().column()
            col.prop(prefs, "sacr_branch", text="Branch")
            col.prop(prefs, "sacr_version", text="Version")
            manifest_exists = os.path.exists(prefs.addon_directory + "/Manifest.json")


            row = col.row(align=True)
            version_dir = os.path.join(prefs.addon_directory, "sacr", prefs.sacr_version)
            if os.path.isdir(version_dir):
                op = row.operator(Prefixer("delete_rig").operator, icon="TRASH", text="Delete")
                op.version = prefs.sacr_version
            else:
                op = row.operator(Prefixer("download_rig").operator, icon="IMPORT", text="Download")
                op.version = prefs.sacr_version


        if prefs.dev_mode:
            box = col.box()
            box.alert = True
            box.label(text="Dev Mode Enabled", icon="ERROR")
            box.label(text="This mode allows for debugging and testing of the addon. Use with caution.")

            col = box.column()
            col.label(text=f"Selected Version: {prefs.sacr_version}")
            
            from .lib import SacrDownloader
            downloader = SacrDownloader(prefs.sacr_branch)
            remote_link = downloader.get_download_url(prefs.sacr_version) or "Unknown (Manifest missing or version not found)"
            
            col.label(text="Remote Link:")
            col.label(text=remote_link)
            
            col.separator()
            col.label(text="Addon Directory:")
            version_dir = os.path.join(prefs.addon_directory, "sacr", prefs.sacr_version)
            col.label(text=version_dir)
            col.label(text=f"Directory Exists: {os.path.isdir(version_dir)}")



classes = [
    RigManagerPanel,
]

# Registering
def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
