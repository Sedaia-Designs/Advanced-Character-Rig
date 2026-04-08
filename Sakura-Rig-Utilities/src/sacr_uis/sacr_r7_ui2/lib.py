import bpy
import bpy.types as T
from ...preferences import Prefixer

# Global Rig Variables
rig_info = {
    "name": "Sakura's Advanced Character Rig",
    "id": "SACR",
    "version": (7, 4, 1),
}

rig_ver = rig_info['version'][0]
ui_ver = 2

config_objs = {
    "main": "Rig_Properties",
    "face": "Face_Properties",
    "mouth": "Mouth_Properties",
    "eyes": "Eye_Properties",
    "eyebrows": "Eyebrow_Properties",
    "materials": "MaterialEditor",
    "root_bone": "SACR_Root"
}

class ConfigObjs(str):
    main = "Rig_Properties"
    face = "Face_Properties"
    mouth = "Mouth_Properties"
    eyes = "Eye_Properties"
    eyebrows = "Eyebrow_Properties"
    materials = "MaterialEditor"
    root_bone = "SACR_Root"

    def __repr__(self):
        return f"ConfigObjs.{self}"

category = f"{rig_info['id']} R{rig_ver}"

class SACR7_UI2_Panel_Base:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = category

    @classmethod
    def poll(cls, context):
        rig_id = f"{rig_info['id']}.Rev_{rig_ver}.UI_{ui_ver}"
        prop_name = "rigID"
        try:
            r = context.active_object
            if r and r.type == "ARMATURE" and r.data:
                return r.data.get(prop_name) == rig_id
            return False
        except (AttributeError, KeyError, TypeError):
            return False

class SACR7_UI2_Face_Panel_Base(SACR7_UI2_Panel_Base):
    @classmethod
    def poll(cls, context):
        if not super().poll(context):
            return False
        try:
            obj = context.active_object
            face_on = obj.pose.bones[config_objs["main"]]["Face Toggle"]
            return face_on
        except (AttributeError, KeyError, TypeError):
            return False
