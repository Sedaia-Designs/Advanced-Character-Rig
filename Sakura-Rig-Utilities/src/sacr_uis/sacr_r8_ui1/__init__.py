from . import (
    properties,
    PANEL_sacr_8_ui1_global,
    PANEL_sacr_8_ui1_face,
    PANEL_sacr_8_ui1_torso,
    PANEL_sacr_8_ui1_arms,
    PANEL_sacr_8_ui1_legs,
)

modules = [
    properties,
    PANEL_sacr_8_ui1_global,
    PANEL_sacr_8_ui1_face,
    PANEL_sacr_8_ui1_torso,
    PANEL_sacr_8_ui1_arms,
    PANEL_sacr_8_ui1_legs,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
