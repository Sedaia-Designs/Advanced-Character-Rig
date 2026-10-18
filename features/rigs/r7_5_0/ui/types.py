import bpy.types as T


# Naming Convension: SACR_UI<Rig Major Ver><UI Major Ver>_Panel
class SACR_UI750_Panel(T.Panel):
    """
    Represents a UI panel within the 3D Viewport for SACR configuration.

    This class defines a custom UI panel in Blender's 3D Viewport. The panel is
    categorized under "SACR Config". It includes a poll method to check whether
    the active object meets specific criteria before displaying the panel.

    Attributes:
        bl_category: Specifies the label for the panel's tab in the UI.
        bl_space_type: Specifies the Blender editor type where the panel will appear.
        bl_region_type: Specifies the region of the editor where the panel will be located.

    Methods:
        poll(cls, context):
            Determines whether the panel should be displayed based on the context.
    """

    bl_category = "SACR Config"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    # TODO: Test if rig_id can be extracted from the classmethod poll into being a class attribute. Complete this once the UI is stable and reorganized.
    @classmethod
    def poll(self, context):
        """Return whether the current Blender context supports this UI element."""
        rig_id = "SACR.Rev_7.UI_3"
        prop_name = "rigID"

        try:
            r = context.active_object
            if r and r.type == "ARMATURE" and r.data:
                rData = r.data
                return rData[prop_name] == rig_id
            else:
                return False
        except (AttributeError, KeyError, TypeError):
            return False
