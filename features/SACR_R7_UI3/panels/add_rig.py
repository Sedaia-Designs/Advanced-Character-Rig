"""The Add Rig panel, which adds a new SACR R7.5 rig at the 3D Cursor."""

import bpy.types as T

from ....constants import Sidebar
from ..operators.constants import OperatorID
from ..ui.types import SACR_UI750_Panel
from .constants import PanelID


class PT_AddRig(T.Panel):
    """Add a new SACR R7.5 rig. Shown with or without a rig selected."""

    bl_label = "Add Rig"
    bl_idname = PanelID.ADD_RIG
    bl_space_type = Sidebar.SPACE
    bl_region_type = Sidebar.REGION
    bl_category = SACR_UI750_Panel.bl_category
    bl_order = 10

    def draw(self, context):
        """Draw the Add SACR Rig button."""
        layout = self.layout
        layout.operator(OperatorID.ADD_RIG, icon="ARMATURE_DATA")
        layout.label(text="Adds the rig at the 3D Cursor.", icon="PIVOT_CURSOR")


classes = (
    PT_AddRig,
)
