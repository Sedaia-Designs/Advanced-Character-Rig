# Imports
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U

from ..preferences import get_preferences, Prefixer

T.Scene.skins_username = P.StringProperty(name="Username")

class SkinsPanel(T.Panel):
    bl_label = "SACR Skins"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SACR Skins"
    bl_idname = Prefixer("skins_ui").panel

    def draw_header(self, context):
        self.layout.label(text="", icon="TEXTURE_DATA")

    def draw(self, context):
        scene = context.scene
        prefs = get_preferences()
        skin_props = scene.skins

        layout = self.layout

        col = layout.column(align=True)
        col.row().label(text="Download Skin:")
        row = col.row(align=True)
        row.prop(scene, "skins_username", text="")
        row.operator(Prefixer("download_skin").operator, icon="IMPORT", text="")

        layout.separator()

        col = layout.column()
        col.row().label(text="Select Profile:")
        row = col.row(align=True)
        column = row.column(align=True)
        column.template_list("SkinList", "", skin_props, "skins", skin_props, "selected_skin")

        column = row.column(align=True)
        column.operator(Prefixer("refresh_skin_list").operator, icon="FILE_REFRESH", text="")

        
        if skin_props.skins:
            selected_skin = skin_props.skins[skin_props.selected_skin]
            op = column.operator(Prefixer("delete_player").operator, icon="TRASH", text="")
            op.name = selected_skin.name

            op = column.operator(Prefixer("update_player").operator, icon="IMPORT", text="")
            op.name = selected_skin.name

            # Skin Texture Selection
            box = layout.box()
            box.label(text=f"Selected Profile: {selected_skin.name}", icon="USER")
            
            row = box.row(align=True)
            row.prop(selected_skin, "skin_texture_enum", text="Texture")
            op = row.operator(Prefixer("delete_skin").operator, icon="X", text="")
            op.name = selected_skin.name
            op.index = int(selected_skin.skin_texture_enum)
            
            # Options
            col = box.column(align=True)
            col.prop(selected_skin, "sync_arms")
            col.prop(selected_skin, "sync_name")
            col.prop(selected_skin, "sync_cape")
            
            row = box.row(align=True)
            op = row.operator(Prefixer("apply_skin").operator, icon="TEXTURE_DATA", text="Apply Skin")
            op.name = selected_skin.name

            op = row.operator(Prefixer("open_in_viewer").operator, icon="IMAGE_DATA")
            op.name = selected_skin.name

        layout.separator()


classes = [
    SkinsPanel,
]

# Registering
def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)

if __name__ == "__main__":
    register()
