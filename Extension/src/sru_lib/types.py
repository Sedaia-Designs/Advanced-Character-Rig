import bpy.types as T


class GlobalPanel(T.Panel):
    """
    Represents a UI panel within the 3D Viewport for Sakura Rig Utilities.

    This class defines a custom UI panel in Blender's 3D Viewport. The panel is
    categorized under "Rig Utility".

    Attributes:
        bl_category: Specifies the label for the panel's tab in the UI.
        bl_space_type: Specifies the Blender editor type where the panel will appear.
        bl_region_type: Specifies the region of the editor where the panel will be located.

    Methods:
        poll(cls, context):
            Determines whether the panel should be displayed based on the context.
    """

    bl_category = "Rig Utility"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"
