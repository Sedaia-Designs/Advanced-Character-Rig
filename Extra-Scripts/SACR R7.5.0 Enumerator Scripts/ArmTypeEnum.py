#━━━━━━━━━━━━━━━━━━━━
# Script is using adapted code from experimenting done by Endertainer007
#
# This script is meant to make creating Enums in the properties panel,
# without having to deal with Property Polution in the Posebone space,
# which can cause conflicts with rigs using same Property names, such as
# Entertainer MCS3 and SACR R7.4.1 which both use the name "ArmType" for
# defining Arm models
#
# This Script was written with Blender 5.1 in mind, versions prior or after may or may not work
#
#━━━━━━━━━━━━━━━━━━━━
#     Enum_Data
#━━━━━━━━━━━━━━━━━━━━
BONE_NAME: str = "Rig_Properties"
PROPERTY_NAME: str = "Arm Type"
PROPERTY_DESC: str = "What type of arm do you want to use?"
ENUM_ITEMS: list = [
    ("0", "Default", "The default model used in Minecraft, using a 4x4x12 pixel layout"),
    ("1", "Slim", "The slim model used in Minecraft, using a 4x3x12 pixel layout"),
    ("2", "Super-Slim", "A custom, 3x3x12 layout model not found in Minecraft")
]

#━━━━━━━━━━━━━━━━━━━━
#      Process
#━━━━━━━━━━━━━━━━━━━━
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O

obj = bpy.context.active_object
pose_bones = obj.pose.bones

def change_prop():
    BONE = pose_bones[BONE_NAME]
    BONE.id_properties_ui(PROPERTY_NAME).update(
        min=0,
        max=len(ENUM_ITEMS)-1,
        items=ENUM_ITEMS,
        description=PROPERTY_DESC
    )
    BONE.property_overridable_library_set(f'["{PROPERTY_NAME}"]', True)

def create_property():
    BONE = pose_bones[BONE_NAME]
    BONE[PROPERTY_NAME] = 0
    BONE.id_properties_ensure()
    BONE.id_properties_ui(PROPERTY_NAME).update(min=0)

    change_prop()

if __name__ == "__main__":
    try: change_prop()
    except KeyError: create_property()
