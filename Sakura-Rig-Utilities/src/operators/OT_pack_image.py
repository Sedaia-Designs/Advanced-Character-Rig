import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U

from ..lib import ID

class OT_pack_image(T.Operator):
    bl_label = ""
    bl_idname = ID("image_pack").operator
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):
        self.report({"PROPERTY"}, self.path)
        image = bpy.data.images[self.path]
        if image.packed_files:
            if bpy.data.is_saved:
                image.unpack()
            else:
                image.unpack(method="USE_LOCAL")
        else:
            image.pack()
        return {"FINISHED"}

def register():
    U.register_class(OT_pack_image)

def unregister():
    U.unregister_class(OT_pack_image)
