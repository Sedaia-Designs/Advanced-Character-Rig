import bpy.types as T
import bpy.props as P

from bpy.ops import wm

from .constants import OperatorID


class FILE_open(T.Operator):
    bl_label = "Open"
    bl_idname = OperatorID.FILE_OPEN

    path: P.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        if not self.path:
            self.report({"ERROR"}, "No path given to open")
            return {"CANCELLED"}
        wm.path_open(filepath=self.path)
        return {"FINISHED"}


classes = (
    FILE_open,
)
