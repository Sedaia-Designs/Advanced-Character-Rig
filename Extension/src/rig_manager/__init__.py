from importlib import reload

if "Rig_UIList" in locals():
    reload(Rig_UIList)
else:
    from . import Rig_UIList

if "PT_Rig_Manager" in locals():
    reload(PT_Rig_Manager)
else:
    from . import PT_Rig_Manager

if "OT_download_available_riglist" in locals():
    reload(OT_download_available_riglist)
else:
    from . import OT_download_available_riglist

modules = (
    Rig_UIList,
    OT_download_available_riglist,
    PT_Rig_Manager,
)


def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()
