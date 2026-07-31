"""
The Interface package is where all the Global UI elements are stored. These are the panels, menus, and buttons that are displayed in the Blender UI.
"""
import bpy
from ..lib import Prefixer

class SEDAIA_PT_Extension_Test(bpy.types.Panel):
    bl_idname = Prefixer("Extension")
    bl_label = "Sedaia Minecraft Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sedaia"
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.label(text="Sedaia Minecraft Utilities")


def register():
    bpy.utils.register_class(SEDAIA_PT_Extension_Test)

def unregister():
    bpy.utils.unregister_class(SEDAIA_PT_Extension_Test)

if __name__ == "__main__":
    register()