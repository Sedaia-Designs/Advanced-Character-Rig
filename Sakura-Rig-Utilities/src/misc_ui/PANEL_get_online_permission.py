"""
Panel for requesting online permission from the user.
"""

import bpy
import bpy.types as T
import bpy.utils as U

from ..preferences import Prefixer, get_preferences
from ..operators.lib.blender_utils import allow_online


class PANEL_get_online_permission(T.Panel):
    """Panel to request and display online permission status."""
    bl_label = "Online Permissions"
    bl_idname = Prefixer("get_online_permission").panel
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SACR Utils"

    @classmethod
    def poll(self, context):
        return not allow_online()

    def draw(self, context):
        layout = self.layout
        prefs = get_preferences()

        box = layout.box()
        box.alert = True
        box.label(text="Online Functionality", icon='WORLD')

        box.label(text="Status: Disabled", icon='CANCEL')
        box.label(text="Enable in Preferences > System to unlock")
        box.label(text="the full feature set, which includes:")

        box.separator()
        box.label(text="Online features include:")
        box.label(text="Download the latest SACR Builds", icon='DISCLOSURE_TRI_RIGHT')
        box.label(text="Download Minecraft Skins and Capes", icon='DISCLOSURE_TRI_RIGHT')



def register():
    U.register_class(PANEL_get_online_permission)


def unregister():
    U.unregister_class(PANEL_get_online_permission)


if __name__ == "__main__":
    register()
