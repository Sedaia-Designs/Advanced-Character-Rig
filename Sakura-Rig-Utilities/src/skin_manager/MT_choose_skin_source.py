# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import Prefixer
from ..operators.lib.blender_utils import allow_online

class ChooseSkinSource(T.Operator):
    bl_label = "Add Skin / Profile"
    bl_idname = Prefixer("choose_skin_source").operator
    bl_description = "Add a new skin to a profile or create a new skin profile"

    action: P.EnumProperty(
        name="Action",
        items=[
            ('IMPORT', "Import", "Import a skin from a local file"),
            ('DOWNLOAD', "Download", "Download a skin from Mojang"),
        ],
        default='IMPORT',
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "sacr_skins_username", text="Username")

        if allow_online():
            layout.label(text="Source")
            layout.prop(self, "action", text="Action", expand=True)
        else:
            # Automatically pass the action as IMPORT if offline
            self.action = 'IMPORT'


    def execute(self, context):
        username = context.scene.sacr_skins_username
        if not username:
            self.report({'ERROR'}, "Please enter a username first")
            return {'CANCELLED'}

        # Ensure refreshing the skin list if any action is taken
        def refresh():
            if hasattr(O.sedaia_rigs_ot, "refresh_skin_list"):
                O.sedaia_rigs_ot.refresh_skin_list()

        if self.action == 'IMPORT':
            # This calls the ImportSkinFile operator which has its own dialog (ImportHelper)
            return O.sedaia_rigs_ot.import_skin_file('INVOKE_DEFAULT')
        
        elif self.action == 'DOWNLOAD':
            if not allow_online():
                self.report({'ERROR'}, "Online functionality is disabled.")
                return {'CANCELLED'}

            res = O.sedaia_rigs_ot.download_skin()
            refresh()
            return res

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Registering
def register():
    U.register_class(ChooseSkinSource)


def unregister():
    U.unregister_class(ChooseSkinSource)


if __name__ == "__main__":
    register()
