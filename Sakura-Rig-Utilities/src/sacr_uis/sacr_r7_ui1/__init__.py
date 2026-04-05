from . import (
    PANEL_sacr_7_ui1_global,
    PANEL_sacr_7_ui1_face,
)

modules = [
    PANEL_sacr_7_ui1_global,
    PANEL_sacr_7_ui1_face,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
