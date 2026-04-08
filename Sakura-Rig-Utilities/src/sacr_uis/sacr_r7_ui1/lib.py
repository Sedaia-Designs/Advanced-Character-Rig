import bpy
import bpy.types as T
from ...preferences import Prefixer

# Global Rig Variables
rig = "SACR"
rig_ver = 7
ui_ver = 1
category = f"{rig} R{rig_ver}"
id_prop = "sacr_id"
id_str = [
    "SACR.Rev_7",  # SACR R7.3 and Newer
    "sacr_1",  # SACR R7.2.1 and older
]
mesh_mat_obj = "MaterialEditor"

class SACR7_UI1_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(cls, context):
        try:
            obj = context.active_object
            if obj and obj.type == "ARMATURE" and obj.data:
                armature = obj.data
                return armature.get(id_prop) in id_str
            return False
        except (AttributeError, KeyError, TypeError):
            return False

class SACR7_UI1_Face_Panel_Base(SACR7_UI1_Panel_Base):
    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        try:
            obj = context.active_object
            face_on = obj.pose.bones["Rig_Properties"]["Face Toggle"]
            return face_on
        except (AttributeError, KeyError, TypeError):
            return False
