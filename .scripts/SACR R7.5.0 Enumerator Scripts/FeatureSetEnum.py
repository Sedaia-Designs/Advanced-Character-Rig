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
PROPERTY_NAME: str = "feature_set"
PROPERTY_DESC: str = "Utilized by the Python UI to enable or disble features for each build of the rig."
ENUM_ITEMS: list = [
    ("0", "Standard", "The standard, full feature build of the rig."),
    ("1", "Lite", "A stripped down, lightweight version of the Rig, choosing this mode disables certain features within the SACR Python UI"),
    # ("2", "Python", "Reveals an additional bone which handles all the Python related interfaces")
]

#━━━━━━━━━━━━━━━━━━━━
#      Process
#━━━━━━━━━━━━━━━━━━━━
import bpy

def change_prop(DATA):
    """Update prop."""
    DATA.id_properties_ui(PROPERTY_NAME).update(
        min=0,
        max=len(ENUM_ITEMS)-1,
        items=ENUM_ITEMS,
        description=PROPERTY_DESC
    )
    DATA.property_overridable_library_set(f'["{PROPERTY_NAME}"]', True)

def create_property(DATA):
    """Create property."""
    DATA[PROPERTY_NAME] = 0
    DATA.id_properties_ensure()
    DATA.id_properties_ui(PROPERTY_NAME).update(min=0)

    change_prop(DATA)

if __name__ == "__main__":
    obj = bpy.context.active_object
    target = obj.data

    try: change_prop(target)
    except KeyError: create_property(target)
