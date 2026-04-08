import bpy
import bpy.types as T
from ...preferences import Prefixer

# Global Rig Variables
rig_ver = 8
ui_ver = 1
mat_obj_name = "MaterialEditor"
prop_bones = [
    "Properties.RigMain",
    "Properties.Arms",
    "Properties.Legs",
    "Properties.Torso",
    "Properties.Head",
]

class SACR8_UI1_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SACR"

    @classmethod
    def poll(cls, context):
        try:
            obj = context.active_object
            if obj and obj.type == "ARMATURE" and obj.data:
                armature = obj.data
                return armature.get("sacr_id") == "SACR.Rev_8"
            return False
        except (AttributeError, KeyError, TypeError):
            return False
