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

    import_mode: P.StringProperty(
        name="Import Mode",
        description="The import mode to use when appending the rig",
        default="BASE"
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        # Main Rig List check
        rig_props = scene.sacr_rigs
        if rig_props.sacr_rigs and rig_props.selected_rig < len(rig_props.sacr_rigs):
             return True
        
        # Rig Presets List check
        preset_props = scene.sacr_rig_presets
        if preset_props.presets and preset_props.selected_preset < len(preset_props.presets):
            return True
            
        return False

    def execute(self, context):
        scene = context.scene
        rig_props = scene.sacr_rigs
        preset_props = scene.sacr_rig_presets
        
        rig_item = None
        
        # Priority 1: Check main rig list if it has a valid selection
        if self.import_mode == "BASE":
            if rig_props.sacr_rigs and 0 <= rig_props.selected_rig < len(rig_props.sacr_rigs):
                rig_item = rig_props.sacr_rigs[rig_props.selected_rig]
        elif self.import_mode == "PRESET":
            # Priority 2: Check preset list if it has a valid selection
            if preset_props.presets and 0 <= preset_props.selected_preset < len(preset_props.presets):
                rig_item = preset_props.presets[preset_props.selected_preset]
        
        if not rig_item:
            self.report({'ERROR'}, "No rig selected")
            return {'CANCELLED'}
            
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
