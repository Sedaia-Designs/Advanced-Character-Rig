# Imports
import bpy.types as T
import bpy.props as P
import bpy.utils as U

class RigItem(T.PropertyGroup):
    name: P.StringProperty(name="Name")
    id: P.StringProperty(name="ID")
    version: P.StringProperty(name="Version")
    branch: P.StringProperty(name="Branch")
    filepath: P.StringProperty(name="Filepath")

class RigListProperties(T.PropertyGroup):
    sacr_rigs_collection: P.CollectionProperty(type=RigItem)
    selected_rig: P.IntProperty(name="Selected Rig", default=0)

from ..lib import ID

class RigList(T.UIList):
    bl_idname = ID(rig_list).list

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name, icon='ARMATURE_DATA')

# Register and unregister classes
classes = (
    # Type the Class Name here
    RigItem,
    RigListProperties,
    RigList,
)


def register():
    for cls in classes:
        U.register_class(cls)

    T.Scene.sacr_rigs = P.PointerProperty(type=RigListProperties)


def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)

    del T.Scene.sacr_rigs
