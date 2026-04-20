# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U
from ..preferences import Prefixer

class RigPresetItem(T.PropertyGroup):
    name: P.StringProperty(name="Name")
    filepath: P.StringProperty(name="Filepath")

class RigPresetListProperties(T.PropertyGroup):
    def update_selected_preset(self, context):
        if not self.presets:
            return
        
        idx = self.selected_preset
        if 0 <= idx < len(self.presets):
            self.new_preset_name = self.presets[idx].name

    presets: P.CollectionProperty(type=RigPresetItem)
    selected_preset: P.IntProperty(
        name="Selected Preset",
        default=0,
        update=update_selected_preset
    )
    new_preset_name: P.StringProperty(name="New Preset Name", default="MyPreset")

class RigPresetList(T.UIList):
    bl_idname = Prefixer("rig_preset_list").list
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon="FILE_BLEND")

classes = [
    RigPresetItem,
    RigPresetListProperties,
    RigPresetList
]

# Registering
def register():
    for cls in classes:
        U.register_class(cls)

    T.Scene.sacr_rig_presets = P.PointerProperty(type=RigPresetListProperties)

def unregister():
    for cls in classes:
        U.unregister_class(cls)

    del T.Scene.sacr_rig_presets

if __name__ == "__main__":
    register()
