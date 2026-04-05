# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer

class RefreshRigList(T.Operator):
    bl_idname = Prefixer("refresh_rig_list").operator
    bl_label = "Refresh Rig List"
    bl_description = "Refresh the rig list"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            from .lib import RigFinder
            prefs = get_preferences()
            addon_dir = prefs.addon_directory

            finder = RigFinder(addon_dir)
            finder.scan_for_rigs()

            scene = context.scene
            rig_props = scene.rigs

            # Clear existing rigs
            rig_props.rigs.clear()

            for rig in finder.rig_data:
                item = rig_props.rigs.add()
                item.name = rig["name"]
                item.filepath = rig["filepath"]
                
            self.report({'INFO'}, f"Refreshed rig list: {len(finder.rig_data)} rigs found.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh rig list: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Registering
def register():
    U.register_class(RefreshRigList)


def unregister():
    U.unregister_class(RefreshRigList)


if __name__ == "__main__":
    register()
