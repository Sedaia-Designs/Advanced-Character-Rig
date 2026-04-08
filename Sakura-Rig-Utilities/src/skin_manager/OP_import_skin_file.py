# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from bpy_extras.io_utils import ImportHelper

from ..preferences import Prefixer
from .lib.skin_utils import SkinUtils

class ImportSkinFile(T.Operator, ImportHelper):
    bl_label = "Import Skin File"
    bl_idname = Prefixer("import_skin_file").operator
    bl_description = "Import a skin file from your computer"

    filename_ext = ".png"

    filter_glob: P.StringProperty(
        default="*.png;*.jpg;*.jpeg",
        options={'HIDDEN'},
        maxlen=255,
    )

    model: P.EnumProperty(
        name="Model",
        items=[
            ('0', "Default", "Default Steve model"),
            ('1', "Slim", "Slim Alex model"),
        ],
        default='0',
    )

    def execute(self, context):
        username = context.scene.skins_username
        if not username:
            self.report({'ERROR'}, "Username is required")
            return {'CANCELLED'}

        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}

        utils = SkinUtils(username)
        result = utils.import_skin(self.filepath, model=self.model)

        if result == 'complete_new':
            self.report({'INFO'}, f"New profile created for {username}")
            # Refresh skin list if possible
            if hasattr(O.sedaia_rigs_ot, "refresh_skin_list"):
                O.sedaia_rigs_ot.refresh_skin_list()
            return {'FINISHED'}
        elif result == 'complete_added':
            self.report({'INFO'}, f"Skin added to existing profile for {username}")
            # Refresh skin list if possible
            if hasattr(O.sedaia_rigs_ot, "refresh_skin_list"):
                O.sedaia_rigs_ot.refresh_skin_list()
            return {'FINISHED'}
        elif result == 'already_cached':
            self.report({'WARNING'}, "This skin is already imported for this user")
            return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "Failed to import skin")
            return {'CANCELLED'}

# Registering
def register():
    U.register_class(ImportSkinFile)

def unregister():
    U.unregister_class(ImportSkinFile)

if __name__ == "__main__":
    register()
