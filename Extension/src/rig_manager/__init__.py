from . import PT_Rig_Manager
from . import OT_download_available_riglist
modules = (
    OT_download_available_riglist,
    PT_Rig_Manager,
)


def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
