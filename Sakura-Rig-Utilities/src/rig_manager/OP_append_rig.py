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
        
        from .lib import RigFinder
        success, message = RigFinder.append_rig(rig_item)
        
        if success:
            self.report({'INFO'}, message)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

# Registering
def register():
    U.register_class(AppendRig)

def unregister():
    U.unregister_class(AppendRig)

if __name__ == "__main__":
    register()
