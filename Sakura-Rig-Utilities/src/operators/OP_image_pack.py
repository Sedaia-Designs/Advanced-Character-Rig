import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from ..preferences import Prefixer
from .lib import blender_utils as utils

class OP_image_pack(T.Operator):
    """Pack or unpack an image into the Blender file."""
    bl_label = "Pack/Unpack Image"
    bl_idname = Prefixer("image_pack").operator
    bl_options = {'REGISTER', 'UNDO'}

    path: P.StringProperty(
        name="Image Name",
        description="Name of the image in Blender data to pack/unpack",
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

            if utils.is_packed(image):
                if bpy.data.is_saved:
                    image.unpack()
                else:
                    image.unpack(method="USE_LOCAL")
            else:
                image.pack()

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to (un)pack image: {e}")
            return {'CANCELLED'}

def register():
    U.register_class(OP_image_pack)

def unregister():
    U.unregister_class(OP_image_pack)
