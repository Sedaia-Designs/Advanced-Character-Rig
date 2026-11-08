import bpy.types as T
import bpy.props as P

from bpy.ops import wm

from .. import prefs
from .constants import OperatorID


class FILE_open(T.Operator):
    bl_label = "Open"
    bl_idname = OperatorID.FILE_OPEN

    path: P.StringProperty(default=prefs.config['root_default_dir'])

    def execute(self, context):
        wm.path_open(filepath=self.path)
        return {"FINISHED"}

classes = (
    FILE_open,
)
