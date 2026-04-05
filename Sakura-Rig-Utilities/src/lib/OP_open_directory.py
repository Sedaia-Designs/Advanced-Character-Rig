import bpy.types as T
import bpy.utils as U
import bpy.ops as O
from ..preferences import Prefixer, get_preferences

class OpenDirectory(T.Operator):
    bl_idname = Prefixer("open_directory").operator
    bl_label = "Open Directory"

    def execute(self, context):
        O.wm.path_open(filepath=get_preferences().addon_directory)
        return {'FINISHED'}

classes = [
    OpenDirectory,
]

def register():
    U.register_class(OpenDirectory)

def unregister():
    U.unregister_class(OpenDirectory)