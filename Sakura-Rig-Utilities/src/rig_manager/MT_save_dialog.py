# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import Prefixer, get_preferences


class SaveDialog(T.Menu):
    bl_idname = Prefixer("save_dialog").menu
    bl_label = "Save Dialog"
    bl_description = "Save the current file"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.operator(Prefixer("save_rig_preset").operator, icon='FILE_TICK')
        layout.separator()
        layout.operator("wm.save_as_mainfile", text="Save As", icon='FILE_TICK')
        layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')
        layout.operator("wm.revert_mainfile", text="Revert", icon='FILE_REFRESH')


# Registering
def register():
    U.register_class(SaveDialog)


def unregister():
    U.unregister_class(SaveDialog)


if __name__ == "__main__":
    register()
