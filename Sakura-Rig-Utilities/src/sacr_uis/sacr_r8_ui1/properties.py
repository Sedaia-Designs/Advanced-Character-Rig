import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U

# R8 UI1 currently doesn't seem to have specialized property synchronization like UI2
# but we follow the structure.

class SACR_R8_UI1_Properties(T.PropertyGroup):
    # We can add properties here if we want to move them from PoseBone to Object in the future
    # for now, the attached file still uses PoseBone for most things.
    pass

def register():
    U.register_class(SACR_R8_UI1_Properties)
    T.Object.sacr_r8_ui1_props = P.PointerProperty(type=SACR_R8_UI1_Properties)

def unregister():
    del T.Object.sacr_r8_ui1_props
    U.unregister_class(SACR_R8_UI1_Properties)
