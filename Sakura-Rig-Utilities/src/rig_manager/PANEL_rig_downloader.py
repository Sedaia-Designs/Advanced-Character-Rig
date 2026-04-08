
from ..preferences import Prefixer, get_preferences
from ..operators.lib.blender_utils import allow_online


def rig_downloader(layout):

    download_panel = layout.panel(idname=Prefixer("download_panel").panel, default_closed=True)

    header = download_panel[0]
    header.label(text="Downloader", icon="IMPORT")

    content = download_panel[1]
    if content is not None:
        if not allow_online():
            layout.label(text="Online functionality is disabled in Blender settings.", icon="ERROR")
        else:
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