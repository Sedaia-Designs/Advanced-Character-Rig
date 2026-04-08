import bpy

# Global Rig Variables
rig_ver = 8
ui_ver = 1
mat_obj_name = "MaterialEditor"
prop_bones = [
    ConfigObjs.main,
    ConfigObjs.arm,
    ConfigObjs.leg,
    ConfigObjs.torso,
    ConfigObjs.head,
]

class ConfigObjs(str):
    main = "Properties.RigMain"
    arm = "Properties.Arms"
    leg = "Properties.Legs"
    torso = "Properties.Torso"
    head = "Properties.Head"

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
