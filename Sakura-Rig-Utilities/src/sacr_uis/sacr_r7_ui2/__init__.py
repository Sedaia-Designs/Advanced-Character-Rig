from . import (
    properties,
    PANEL_sacr_7_ui2_global_main,
    PANEL_sacr_7_ui2_head,
    PANEL_sacr_7_ui2_torso,
    PANEL_sacr_7_ui2_arm,
    PANEL_sacr_7_ui2_quick_parent,
    PANEL_sacr_7_ui2_armor,
    PANEL_sacr_7_ui2_face_main,
    PANEL_sacr_7_ui2_eyebrows,
    PANEL_sacr_7_ui2_eyes,
    PANEL_sacr_7_ui2_iris,
    PANEL_sacr_7_ui2_sclera,
    PANEL_sacr_7_ui2_mouth,
)

modules = [
    properties,
    PANEL_sacr_7_ui2_global_main,
    PANEL_sacr_7_ui2_head,
    PANEL_sacr_7_ui2_torso,
    PANEL_sacr_7_ui2_arm,
    PANEL_sacr_7_ui2_quick_parent,
    PANEL_sacr_7_ui2_armor,
    PANEL_sacr_7_ui2_face_main,
    PANEL_sacr_7_ui2_eyebrows,
    PANEL_sacr_7_ui2_eyes,
    PANEL_sacr_7_ui2_iris,
    PANEL_sacr_7_ui2_sclera,
    PANEL_sacr_7_ui2_mouth,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
