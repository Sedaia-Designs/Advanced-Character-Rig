"""
The Interface package is where all the Global UI elements are imported into the main project. These are the panels, menus, and buttons that are displayed in the Blender UI.
"""

from importlib import reload

if "sacr_r750" in locals():
    reload(sacr_r750)
else:
    from . import sacr_r750

modules = [sacr_r750]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()
