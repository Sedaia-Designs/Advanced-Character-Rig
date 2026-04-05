from . import (
    PANEL_rig_manager,
    OP_download_rig,
    OP_download_manifest,
    UI_RigList,
    OP_refresh_rig_list,
    OP_append_rig,
    UI_PresetList,
    OP_preset_operators,
    OP_save_rig_preset,
)

modules = [
    OP_download_rig,
    OP_download_manifest,
    UI_RigList,
    OP_refresh_rig_list,
    OP_append_rig,
    UI_PresetList,
    OP_preset_operators,
    PANEL_rig_manager,
    OP_save_rig_preset,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()