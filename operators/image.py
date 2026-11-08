import bpy
import bpy.types as T
import bpy.props as P

from ..core.images import is_packed
from .constants import OperatorID


class IMAGE_pack(T.Operator):
    bl_label = ""
    bl_idname = OperatorID.IMAGE_PACK
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.path)
        if image is None:
            self.report({"ERROR"}, f"No image named '{self.path}'")
            return {"CANCELLED"}
        if is_packed(image):
            if bpy.data.is_saved:
                image.unpack()
            else:
                image.unpack(method="USE_LOCAL")
        else:
            image.pack()
        return {"FINISHED"}


class IMAGE_reload(T.Operator):
    bl_label = ""
    bl_idname = OperatorID.IMAGE_RELOAD
    bl_options = {"REGISTER", "UNDO"}

    path: P.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.path)
        if image is None:
            self.report({"ERROR"}, f"No image named '{self.path}'")
            return {"CANCELLED"}
        image.reload()
        return {"FINISHED"}

classes = (
    IMAGE_pack,
    IMAGE_reload,
)
