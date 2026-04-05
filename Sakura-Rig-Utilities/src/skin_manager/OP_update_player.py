# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from ..operators.lib.blender_utils import allow_online
from .lib import SkinUtils


class UpdatePlayer(T.Operator):
    bl_idname = Prefixer("update_player").operator
    bl_label = "Update Player Profile"
    bl_description = "Check for new skins and update the player profile"
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(name="Player Name")

    def execute(self, context):
        if not allow_online():
            self.report({'WARNING'}, "Online functionality is disabled in Blender settings.")
            return {'CANCELLED'}

        skin_utils = SkinUtils(self.name)
        result = skin_utils.add_skin()

        if result == 'complete':
            self.report({'INFO'}, f"Profile updated for {self.name}")
        elif result == 'already_cached':
            self.report({'INFO'}, f"Profile already up to date for {self.name}")
        elif result == 'http_error':
            self.report({'ERROR'}, f"Failed to retrieve profile for {self.name}")
            return {'CANCELLED'}

        O.sedaia_rigs_ot.refresh_skin_list()
        return {'FINISHED'}


# Registering
def register():
    U.register_class(UpdatePlayer)


def unregister():
    U.unregister_class(UpdatePlayer)


if __name__ == "__main__":
    register()
