# Imports
import bpy
import bpy.types as T
import bpy.utils as U

from ..preferences import Prefixer

class EnableOnlineAccess(T.Operator):
    bl_label = "Enable Online Access"
    bl_idname = Prefixer("enable_online_access").operator
    bl_description = "Enable Blender's online access setting in User Preferences"

    def execute(self, context):
        try:
            context.preferences.system.use_online_access = True
            self.report({'INFO'}, "Online access enabled")
            return {'FINISHED'}
        except AttributeError:
            self.report({'ERROR'}, "This Blender version does not support the 'use_online_access' preference")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to enable online access: {str(e)}")
            return {'CANCELLED'}

# Registering
def register():
    U.register_class(EnableOnlineAccess)

def unregister():
    U.unregister_class(EnableOnlineAccess)

if __name__ == "__main__":
    register()
