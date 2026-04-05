# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer
from .lib import SkinUtils

class ApplySkin(T.Operator):
    bl_idname = Prefixer("apply_skin").operator
    bl_label = "Apply Skin"
    bl_description = "Apply the selected skin to the active rig"
    bl_options = {'REGISTER', 'UNDO'}

    name: P.StringProperty(name="Skin Name")

    def execute(self, context):
        rig = context.active_object
        if not rig or rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Select an armature first")
            return {'CANCELLED'}

        scene = context.scene
        skin_props = scene.skins
        if not skin_props.skins:
            self.report({'ERROR'}, "No skins found")
            return {'CANCELLED'}

        selected_skin = skin_props.skins[skin_props.selected_skin]
        skin_utils = SkinUtils(selected_skin.name)
        
        success, message = skin_utils.apply_skin(rig, selected_skin)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

# Registering
def register():
    U.register_class(ApplySkin)


def unregister():
    U.unregister_class(ApplySkin)


if __name__ == "__main__":
    register()
