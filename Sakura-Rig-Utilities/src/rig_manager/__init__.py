from . import (
    PANEL_rig_manager,
    OP_download_rig,
    OP_download_manifest,
    UI_RigList,
    OP_RefreshRigList,
    OP_append_rig,
)

modules = [
    OP_download_rig,
    OP_download_manifest,
    UI_RigList,
    OP_RefreshRigList,
    OP_append_rig,
    PANEL_rig_manager,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()