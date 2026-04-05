import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ..preferences import Prefixer

class OP_image_reload(T.Operator):
    """Reload an image from disk."""
    bl_label = "Reload Image"
    bl_idname = Prefixer("image_reload").operator
    bl_options = {'REGISTER', 'UNDO'}

    path: P.StringProperty(
        name="Image Name",
        description="Name of the image in Blender data to reload",
        default=""
    )

    def execute(self, context):
        if not self.path:
            self.report({'WARNING'}, "No image name provided.")
            return {'CANCELLED'}
        
        try:
            image = bpy.data.images.get(self.path)
            if not image:
                self.report({'ERROR'}, f"Image '{self.path}' not found.")
                return {'CANCELLED'}

            image.reload()
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to reload image: {e}")
            return {'CANCELLED'}

def register():
    U.register_class(OP_image_reload)

def unregister():
    U.unregister_class(OP_image_reload)
