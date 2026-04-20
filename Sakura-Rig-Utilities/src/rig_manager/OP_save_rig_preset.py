# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
from pathlib import Path

from ..preferences import Prefixer, get_preferences

class SaveRigPreset(T.Operator):
    bl_idname = Prefixer("save_rig_preset").operator
    bl_label = "Save Rig Preset"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Save the current file as a rig preset"

    def execute(self, context):
        PREFS = get_preferences()
        ADDON_DIR = Path(PREFS.addon_directory)
        SACR_DIR = ADDON_DIR / "SACR" / "sacr_rig_presets"

        scene = context.scene
        preset_props = scene.sacr_rig_presets
        name_input = preset_props.new_preset_name

        if not name_input:
            self.report({'ERROR'}, "Preset name cannot be empty")
            return {'CANCELLED'}

        if name_input.endswith(".blend"):
            name = name_input
        else:
            name = f"{name_input}.blend"

        FILEPATH = SACR_DIR / name

        if not SACR_DIR.exists():
            SACR_DIR.mkdir(parents=True, exist_ok=True)

        bpy.ops.wm.save_as_mainfile(filepath=str(FILEPATH), copy=True)
        self.report({'INFO'}, f"Saved rig preset: {name}")

        # Refresh preset list if possible
        try:
            bpy.ops.sedaia_rigs_ot.refresh_preset_list()
        except Exception:
            pass

        return {'FINISHED'}

# Registering
def register():
    U.register_class(SaveRigPreset)


def unregister():
    U.unregister_class(SaveRigPreset)


if __name__ == "__main__":
    register()
