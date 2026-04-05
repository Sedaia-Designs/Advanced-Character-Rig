import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
import webbrowser
from ..preferences import Prefixer

class OP_open_url(T.Operator):
    """Open a URL in the default web browser."""
    bl_label = "Open URL"
    bl_idname = Prefixer("open_url").operator
    bl_options = {'REGISTER', 'UNDO'}

    url: P.StringProperty(
        name="URL",
        description="URL to open",
        default=""
    )

    def execute(self, context):
        if not self.url:
            self.report({'WARNING'}, "No URL provided.")
            return {'CANCELLED'}
        
        try:
            webbrowser.open(self.url)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to open URL: {e}")
            return {'CANCELLED'}

def register():
    U.register_class(OP_open_url)

def unregister():
    U.unregister_class(OP_open_url)
