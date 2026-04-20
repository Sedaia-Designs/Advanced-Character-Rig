# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from pathlib import Path
from ..preferences import Prefixer, get_preferences

class RefreshPresetList(T.Operator):
    bl_idname = Prefixer("refresh_preset_list").operator
    bl_label = "Refresh Preset List"
    bl_description = "Refresh the list of rig presets from the addon directory"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = get_preferences()
        addon_dir = Path(prefs.addon_directory)
        sacr_dir = addon_dir / "SACR" / "sacr_rig_presets"
        
        scene = context.scene
        rig_presets = scene.sacr_rig_presets
        rig_presets.presets.clear()

        if sacr_dir.exists():
            for file in sorted(sacr_dir.glob("*.blend")):
                item = rig_presets.presets.add()
                item.name = file.stem
                item.filepath = str(file)

        return {'FINISHED'}

class LoadRigPreset(T.Operator):
    bl_idname = Prefixer("load_rig_preset").operator
    bl_label = "Load Rig Preset"
    bl_description = "Load the selected rig preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        rig_presets = scene.sacr_rig_presets
        if not rig_presets.presets:
            self.report({'ERROR'}, "No presets available")
            return {'CANCELLED'}
        
        idx = rig_presets.selected_preset
        if idx < 0 or idx >= len(rig_presets.presets):
            self.report({'ERROR'}, "Invalid selection")
            return {'CANCELLED'}
        
        item = rig_presets.presets[idx]
        filepath = item.filepath
        
        if not Path(filepath).exists():
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}
            
        bpy.ops.wm.open_mainfile(filepath=filepath)
        return {'FINISHED'}

class DeleteRigPreset(T.Operator):
    bl_idname = Prefixer("delete_rig_preset").operator
    bl_label = "Delete Rig Preset"
    bl_description = "Delete the selected rig preset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        rig_presets = scene.sacr_rig_presets
        idx = rig_presets.selected_preset
        
        if idx < 0 or idx >= len(rig_presets.presets):
            return {'CANCELLED'}
            
        item = rig_presets.presets[idx]
        filepath = Path(item.filepath)
        
        if filepath.exists():
            filepath.unlink()
            self.report({'INFO'}, f"Deleted preset: {item.name}")
        
        bpy.ops.sedaia_rigs_ot.refresh_preset_list()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

classes = [
    RefreshPresetList,
    LoadRigPreset,
    DeleteRigPreset
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)
