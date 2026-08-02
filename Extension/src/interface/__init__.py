"""
The Interface package is where all the Global UI elements are stored. These are the panels, menus, and buttons that are displayed in the Blender UI.
"""
from . import sacr_r750

modules = [
    sacr_r750
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
