# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from .lib import SkinUtils


class DeleteSkin(T.Operator):
    bl_idname = Prefixer("delete_skin").operator
    bl_label = "Delete Individual Skin"
    bl_description = "Delete the selected skin texture from the profile"
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(name="Player Name")
    index: P.IntProperty(name="Skin Index")

    def execute(self, context):
        try:
            skin_utils = SkinUtils(self.name)
            result = skin_utils.delete_skin(self.index)

            if result == 'complete':
                self.report({'INFO'}, f"Deleted skin index {self.index} for player: {self.name}")
                O.sedaia_rigs_ot.refresh_skin_list()
            else:
                self.report({'WARNING'}, f"Skin not found: {self.name} index {self.index}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete skin texture: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Registering
def register():
    U.register_class(DeleteSkin)


def unregister():
    U.unregister_class(DeleteSkin)


if __name__ == "__main__":
    register()
