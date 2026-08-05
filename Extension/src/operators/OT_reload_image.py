import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U

from ..sru_lib import ID


class OT_reload_image(T.Operator):
    bl_label = ""
    bl_idname = ID("image_reload").operator
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):

        bpy.data.images[self.path].reload()
        return {"FINISHED"}


def register():
    U.register_class(OT_reload_image)


def unregister():
    U.unregister_class(OT_reload_image)
