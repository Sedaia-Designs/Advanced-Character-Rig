"""Menus used by the skin refresh workflow."""

from bpy.types import Menu

from .constants import MENUS, OPS


class SKIN_menu_purge(Menu):
    bl_idname = MENUS["purge"]
    bl_label = "Confirm Purging of Player Data"

    def draw(self, context):
        """Draw this UI element for the current Blender context."""
        layout = self.layout
        layout.operator(OPS["purge"], text="Backup and Purge").backup = True
        layout.operator(OPS["purge"], text="Purge", icon="ERROR").confirm = True


class SKIN_menu_regen(Menu):
    bl_idname = MENUS["regen"]
    bl_label = "Regenerate Player Data?"

    def draw(self, context):
        """Draw this UI element for the current Blender context."""
        layout = self.layout
        layout.operator(OPS["load"], text="Load Data").index = -1
        layout.operator(OPS["add"], text="Add Entry")
        layout.menu(MENUS["purge"], text="Clean Slate", icon="ERROR")


classes = (SKIN_menu_purge, SKIN_menu_regen)
