# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U

class SkinItem(T.PropertyGroup):
    name: P.StringProperty(name="Name")
    uuid: P.StringProperty(name="UUID")
    json_path: P.StringProperty(name="JSON Path")
    
    # Utility Options
    sync_arms: P.BoolProperty(name="Sync Arm Type", default=True)
    sync_name: P.BoolProperty(name="Set Rig Name to Username", default=True)
    sync_cape: P.BoolProperty(name="Sync Cape Status", default=False)
    
    # Dynamic Skin Selection
    def get_skin_textures(self, context):
        import json
        import os
        items = [("0", "None", "")]
        
        if not self.json_path or not os.path.exists(self.json_path):
            return items
            
        try:
            with open(self.json_path, 'r') as f:
                data = json.load(f)
                skins = data.get("SKINS", [])
                if not skins:
                    return items
                
                items = []
                for skin in skins:
                    # Using custom name if available, otherwise fallback to hash-based name
                    display_name = skin.get("name", f"Skin {skin['index']} ({skin['hash'][:8]})")
                    items.append((str(skin["index"]), display_name, skin["path"]))
                return items
        except:
            return items

    skin_texture_enum: P.EnumProperty(
        name="Skin Texture",
        items=get_skin_textures
    )

class SkinListProperties(T.PropertyGroup):
    skins: P.CollectionProperty(type=SkinItem)
    selected_skin: P.IntProperty(name="Selected Skin", default=0)

from ..preferences import Prefixer

class SkinList(T.UIList):
    bl_idname = Prefixer("skin_list").list
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon="TEXTURE_DATA")

classes = [
    SkinItem,
    SkinListProperties,
    SkinList
]

# Registering
def register():
    for cls in classes:
        U.register_class(cls)

    T.Scene.skins = P.PointerProperty(type=SkinListProperties)

def unregister():
    for cls in classes:
        U.unregister_class(cls)

    del T.Scene.skins


if __name__ == "__main__":
    register()
