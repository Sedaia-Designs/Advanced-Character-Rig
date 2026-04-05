import bpy.types as T
import bpy.utils as U
import bpy.ops as O
from ..preferences import Prefixer, get_preferences

class OpenAddonDirectory(T.Operator):
    bl_idname = Prefixer("open_addon_directory").operator
    bl_label = "Open Directory"

    def execute(self, context):
        O.wm.path_open(filepath=get_preferences().addon_directory)
        return {'FINISHED'}

classes = [
    OpenAddonDirectory,
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)