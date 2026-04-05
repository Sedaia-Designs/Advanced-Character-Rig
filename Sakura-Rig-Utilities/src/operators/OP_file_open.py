import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ..preferences import Prefixer

class OP_file_open(T.Operator):
    """Open a directory or file in the default file browser."""
    bl_label = "Open Path"
    bl_idname = Prefixer("file_open").operator
    bl_options = {'REGISTER', 'UNDO'}

    path: P.StringProperty(
        name="Path",
        description="Path to open",
        default=""
    )

    def execute(self, context):
        if not self.path:
            self.report({'WARNING'}, "No path provided.")
            return {'CANCELLED'}
        
        try:
            bpy.ops.wm.path_open(filepath=self.path)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open path: {e}")
            return {'CANCELLED'}

def register():
    U.register_class(OP_file_open)

def unregister():
    U.unregister_class(OP_file_open)
