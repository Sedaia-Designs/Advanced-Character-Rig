
import bpy.ops as O
import bpy.utils as U
import bpy.types as T

from ..preferences import Prefixer

class open_file(T.Operator):
    bl_label = "Open"
    bl_idname = Prefixer("open_file").operator

    path: StringProperty(default=config["file_path"])

    def execute(self, context):
        O.wm.path_open(filepath=self.path)
        return {"FINISHED"}

def register():
    U.register_class(open_file)

def unregister():
    U.unregister_class(open_file)