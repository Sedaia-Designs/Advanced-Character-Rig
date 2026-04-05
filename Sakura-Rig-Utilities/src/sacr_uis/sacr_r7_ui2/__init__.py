from . import (
    properties,
    PANEL_sacr_7_ui2_global,
    PANEL_sacr_7_ui2_face,
)

modules = [
    properties,
    PANEL_sacr_7_ui2_global,
    PANEL_sacr_7_ui2_face,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
