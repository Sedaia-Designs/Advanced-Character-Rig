

import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
import bpy.ops as O
import os

class SEDAIA_PROPS_Preferences(T.AddonPreferences):
    bl_idname = __package__

    dev_mode : P.BoolProperty(
        name="Developer Mode",
        description="Enable developer mode",
        default=False
    )

    addon_data_location : P.StringProperty(
        name="Addon Data Location",
        description="Location of addon data",
        default=os.path.abspath(U.extension_path_user(
            __package__,
            create=True
        )),
        subtype='DIR_PATH'
    )

    json_data_location : P.StringProperty(
        name="Addon Data Location",
        description="Location of addon data",
        default=os.path.abspath(U.extension_path_user(
            __package__,
            path="json",
            create=True
        )),
        subtype='DIR_PATH'
    )

    sacr_manifest_refresh_interval : P.IntProperty(
        name="Sacr Manifest Refresh Interval",
        description="Interval in seconds for refreshing the manifest",
        default=1
    )

    sacr_manifest_refresh_interval_units : P.EnumProperty(
        name="Sacr Manifest Refresh Interval Units",
        description="Units for the manifest refresh interval",
        items=[
            ("minutes", "Minutes", "Minutes"),
            ("hours", "Hours", "Hours"),
            ("days", "Days", "Days"),
        ],
        default="hours"
    )

    online_access_timeout : P.IntProperty(
        name="Online Access Timeout",
        min=0,
        default=5,
        description="Time limit in seconds for online access",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "dev_mode")
        layout.prop(self, "addon_data_location")
        layout.prop(self, "online_access_timeout")

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences

class_list = [
    SEDAIA_PROPS_Preferences
]

def register():
    for cls in class_list:
        U.register_class(cls)

def unregister():
    for cls in class_list:
        U.unregister_class(cls)

if __name__ == "__main__":
    register()