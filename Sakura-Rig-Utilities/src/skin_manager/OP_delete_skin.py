# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from .lib import SkinUtils

class DeletePlayer(T.Operator):
    bl_idname = Prefixer("delete_player").operator
    bl_label = "Delete Player Profile"
    bl_description = "Delete the selected player profile and all associated sacr_skins_collection"
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(name="Player Name")

    def execute(self, context):
        try:
            skin_utils = SkinUtils(self.name)
            result = skin_utils.delete_player()

            if result == 'complete':
                self.report({'INFO'}, f"Deleted player: {self.name}")
                O.sedaia_rigs_ot.refresh_skin_list()
            else:
                self.report({'WARNING'}, f"Skin not found: {self.name}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete skin: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Registering
def register():
    U.register_class(DeletePlayer)


def unregister():
    U.unregister_class(DeletePlayer)


if __name__ == "__main__":
    register()
