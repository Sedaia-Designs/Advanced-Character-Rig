# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
import os

from ..preferences import Prefixer

class AppendRig(T.Operator):
    bl_idname = Prefixer("append_rig").operator
    bl_label = "Append"
    bl_description = "Append the selected rig collection from its source file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        rig_props = context.scene.rigs
        return (rig_props.rigs and 
                rig_props.selected_rig < len(rig_props.rigs))

    def execute(self, context):
        rig_props = context.scene.rigs
        selected_index = rig_props.selected_rig
        
        if selected_index < 0 or selected_index >= len(rig_props.rigs):
            self.report({'ERROR'}, "Invalid selection")
            return {'CANCELLED'}
            
        rig_item = rig_props.rigs[selected_index]
        rig_name = rig_item.name
        filepath = os.path.abspath(rig_item.filepath)
        
        if not os.path.exists(filepath):
            # Try to see if it's a relative path from addon_dir
            from ..preferences import get_preferences
            prefs = get_preferences()
            alt_path = os.path.abspath(os.path.join(prefs.addon_directory, rig_item.filepath))
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                self.report({'ERROR'}, f"Source file not found: {filepath}")
                return {'CANCELLED'}

        # To append a collection, we use bpy.ops.wm.append or bpy.data.libraries.load
        # Using libraries.load allows more control, but wm.append is simpler for operators
        
        # We need the directory inside the blend file
        directory = os.path.join(filepath, "Collection")
        inner_filepath = os.path.join(directory, rig_name)
        
        try:
            O.wm.append(
                filepath=inner_filepath,
                directory=directory,
                filename=rig_name
            )
            self.report({'INFO'}, f"Appended rig: {rig_name}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to append: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Registering
def register():
    U.register_class(AppendRig)

def unregister():
    U.unregister_class(AppendRig)

if __name__ == "__main__":
    register()
