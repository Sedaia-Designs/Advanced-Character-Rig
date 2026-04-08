from . import (
    PANEL_sacr_7_ui1_global_main,
    PANEL_sacr_7_ui_1_bone_groups,
    PANEL_sacr_7_ui_1_arms,
    PANEL_sacr_7_ui_1_legs,
    PANEL_sacr_7_ui_1_face_main,
    PANEL_sacr_7_ui_1_eyebrows,
    PANEL_sacr_7_ui_1_eyes,
    PANEL_sacr_7_ui_1_irises,
    PANEL_sacr_7_ui_1_pupils,
    PANEL_sacr_7_ui_1_sclera,
    PANEL_sacr_7_ui_1_mouth,
)

modules = [
    PANEL_sacr_7_ui1_global_main,
    PANEL_sacr_7_ui_1_bone_groups,
    PANEL_sacr_7_ui_1_arms,
    PANEL_sacr_7_ui_1_legs,
    PANEL_sacr_7_ui_1_face_main,
    PANEL_sacr_7_ui_1_eyebrows,
    PANEL_sacr_7_ui_1_eyes,
    PANEL_sacr_7_ui_1_irises,
    PANEL_sacr_7_ui_1_pupils,
    PANEL_sacr_7_ui_1_sclera,
    PANEL_sacr_7_ui_1_mouth,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()
