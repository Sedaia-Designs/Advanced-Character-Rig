import bpy
import bpy.types as T
import bpy.props as P
import bpy.utils as U

def get_arm_type(self):
    rig = self.id_data
    if rig and rig.type == 'ARMATURE' and rig.pose:
        bone = rig.pose.bones.get("Rig_Properties")
        if bone and "ArmType" in bone:
            try:
                return int(bone["ArmType"])
            except (ValueError, TypeError):
                pass
    return int(self.get("_arm_type", 0))

def set_arm_type(self, value):
    self["_arm_type"] = value
    rig = self.id_data
    if rig and rig.type == 'ARMATURE' and rig.pose:
        bone = rig.pose.bones.get("Rig_Properties")
        if bone:
            bone["ArmType"] = value

def get_eyelashes(self):
    rig = self.id_data
    if rig and rig.type == 'ARMATURE' and rig.pose:
        bone = rig.pose.bones.get("Eye_Properties")
        if bone and "Eyelashes" in bone:
            try:
                return int(bone["Eyelashes"])
            except (ValueError, TypeError):
                pass
    return int(self.get("_eyelashes", 1))

def set_eyelashes(self, value):
    self["_eyelashes"] = value
    rig = self.id_data
    if rig and rig.type == 'ARMATURE' and rig.pose:
        bone = rig.pose.bones.get("Eye_Properties")
        if bone:
            bone["Eyelashes"] = value

class SACR_R7_UI2_Properties(T.PropertyGroup):
    rig_name: P.StringProperty(
        name="Rig Name",
        default="",
        description="Custom name for the rig"
    )

    arm_type: P.EnumProperty(
        name="Arm Type",
        description="Select your Arm Dimension",
        items=[
            ("0", "Standard", "Standard Arm Style, formerly called Steve Arms"),
            ("1", "Slim", "Slim Arm Style, formerly called Steve Arms"),
            ("2", "Super-Slim",
             "Super Slim Arm style are a 3x3 version not available in Minecraft")
        ],
        get=get_arm_type,
        set=set_arm_type
    )

    eyelashes: P.EnumProperty(
        name="Lash Type",
        description="What style Eyelashes you want",
        items=[
            ("0", "None", ""),
            ("1", "Classic", ""),
            ("2", "SACR", ""),
            ("3", "Flat", ""),
            ("4", "Enchanted Mob", ""),
            ("5", "DanoBandi", ""),
        ],
        get=get_eyelashes,
        set=set_eyelashes
    )

def register():
    U.register_class(SACR_R7_UI2_Properties)
    T.Object.sacr_r7_ui2_props = P.PointerProperty(type=SACR_R7_UI2_Properties)

def unregister():
    del T.Object.sacr_r7_ui2_props
    U.unregister_class(SACR_R7_UI2_Properties)
