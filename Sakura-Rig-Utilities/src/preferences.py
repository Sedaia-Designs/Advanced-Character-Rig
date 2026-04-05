# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
import os

def get_manifest_key(key):
    """Get a key from the blender_manifest.toml file."""
    import os
    import re

    # Path to blender_manifest.toml
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "blender_manifest.toml")

    if not os.path.exists(manifest_path):
        return ""

    with open(manifest_path, 'r') as f:
        content = f.read()

    # Very simple TOML parser for basic keys (string/int)
    # Match key = "value" or key = value
    match = re.search(rf'^{key}\s*=\s*"?([^"\n]+)"?', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return ""

class Prefixer(str):
    @property
    def panel(self):
        return f"SEDAIA_RIGS_PT_{self}"

    @property
    def operator(self):
        return f"sedaia_rigs_ot.{self}"

    @property
    def menu(self):
        return f"SEDAIA_RIGS_MT_{self}"

    @property
    def list(self):
        return f"SEDAIA_RIGS_UL_{self}"

class AddonPreferences(T.AddonPreferences):
    bl_idname = __package__
    bl_label = "Addon Preferences"

    dev_mode : P.BoolProperty(
        name="Developer Mode",
        default=False,
        description=(
            "Enables developer mode, toggling extra debug information and options for Extension Developers."
        )
    )

    addon_directory : P.StringProperty(
        name="Addon Directory",
        subtype='DIR_PATH',
        default=os.path.abspath(U.extension_path_user(
            __package__,
            create=True
        )),
        description=(
            "Directory where the addon data will be downloaded and stored."
        )
    )

    sacr_manifest_refresh_interval : P.IntProperty(
        name="Manifest Refresh Interval",
        default=24,
        min=1,
        max=168,
        description=(
            "Interval in hours for automatic manifest refresh. Set to 0 to disable automatic refresh."
        )
    )

    last_manifest_refresh : P.FloatProperty(
        name="Last Manifest Refresh",
        default=0.0,
        description="Timestamp of the last manifest refresh"
    )

    def sacr_branch_update(self, context):
        """Update callback for sacr_branch to reset sacr_version."""
        items = self.sacr_version_items(context)
        if items:
            # Set sacr_version to the first available item's identifier
            setattr(self, "sacr_version", items[0][0])

    sacr_branch : P.EnumProperty(
        name="SACR Branch",
        items=(
            ("0", "Stable", "Stable branch"),
            ("1", "Dev", "Development branch"),
        ),
        default="0",
        description=(
            "Select the branch of SACR you want to use. Stable branch is recommended for most users, while the Development branch may contain unstable features and bugs and should only be used for testing."
        ),
        update=sacr_branch_update
    )

    def sacr_version_items(self, context):
        import json
        import os
        
        items = [("0", "None", "No versions available")]
        
        manifest_path = os.path.join(self.addon_directory, "Manifest.json")
        if not os.path.exists(manifest_path):
            return items
            
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            return items
            
        sacr = data.get("SACR", {})
        branches = sacr.get("branches", {})
        branch_key = "stable" if self.sacr_branch == "0" else "dev"
        branch_info = branches.get(branch_key, {})
        versions = branch_info.get("versions", [])
        
        if not versions:
            return items
            
        items = []
        for i, v in enumerate(versions):
            version_str = v.get("version", "Unknown")
            # Using index as identifier to ensure it's a valid EnumProperty key
            items.append((version_str, version_str, f"Release Date: {v.get('date', 'Unknown')}"))
            
        return items

    sacr_version : P.EnumProperty(
        name="SACR Version",
        items=sacr_version_items,
        description="Select the version of SACR to download"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Addon Preferences", icon="PREFERENCES")


        row = layout.row()
        col = row.column()
        box = col.box()
        box.label(text="Addon Directory")
        box.prop(self, "addon_directory", text="")
        box.prop(self, "dev_mode", toggle=True, text="Extended Debug Info", icon="CHECKBOX_HLT" if self.dev_mode else "CHECKBOX_DEHLT")

        col = row.column()
        box = col.box()
        box.label(text="SACR Settings")
        box.prop(self, "sacr_branch", text="Branch")
        box.prop(self, "sacr_version", text="Version")

        version_dir = os.path.join(self.addon_directory, "sacr", self.sacr_version)
        if os.path.isdir(version_dir):
            op = box.operator(Prefixer("delete_rig").operator, icon="TRASH", text="Delete")
            op.version = self.sacr_version
        else:
            op = box.operator(Prefixer("download_rig").operator, icon="IMPORT", text="Download")
            op.version = self.sacr_version

        if bpy.app.online_access:
            row = box.row(align=True)
            row.prop(self, "sacr_manifest_refresh_interval", text="Manifest Refresh Interval (Hours)")
            row.operator(Prefixer("download_manifest").operator, icon="FILE_REFRESH", text="")

        if self.dev_mode:
            import datetime
            last_refresh = datetime.datetime.fromtimestamp(self.last_manifest_refresh)
            box.label(text=f"Last Refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

        if self.sacr_branch == "1":
            row = box.row()
            row.alert = True
            row.label(text="Dev branch may be unstable.", icon="ERROR")


        row = layout.row()

        row_issue = row.row(align=True)
        row_issue.operator(Prefixer("copy_debug_info").operator, icon="FILE_TICK", text="Copy Debug Info")
        op = row_issue.operator(Prefixer("open_url").operator, icon="URL", text="Report Issue")
        op.url = get_manifest_key("issue_tracker")

        row_general = row.row(align=True)
        op = row_general.operator(Prefixer("open_url").operator, icon="URL", text="Open Repository")
        op.url = get_manifest_key("github")

        op = row_general.operator(Prefixer("open_url").operator, icon="WORLD", text="Website")
        op.url = get_manifest_key("website")

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences

def check_manifest_refresh():
    """Timer function to check if the manifest needs to be refreshed."""
    import time
    prefs = get_preferences()
    interval_hours = prefs.sacr_manifest_refresh_interval
    
    if interval_hours <= 0:
        return 3600.0 # Check again in an hour
        
    last_refresh = prefs.last_manifest_refresh
    current_time = time.time()
    
    # Calculate elapsed time in hours
    elapsed_hours = (current_time - last_refresh) / 3600.0
    
    if elapsed_hours >= interval_hours:
        try:
            bpy.ops.sedaia_rigs_ot.download_manifest()
        except Exception:
            return 300.0 # Retry in 5 minutes if it failed
            
    # Calculate time until next refresh
    try:
        prefs = get_preferences()
        time_until_next = (interval_hours - (current_time - prefs.last_manifest_refresh) / 3600.0) * 3600.0
    except Exception:
        time_until_next = interval_hours * 3600.0
    # Don't check more often than every 5 minutes, but not less than every hour
    return max(300.0, min(time_until_next, 3600.0))

# Registering
def register():
    U.register_class(AddonPreferences)


def unregister():
    U.unregister_class(AddonPreferences)


if __name__ == "__main__":
    register()
