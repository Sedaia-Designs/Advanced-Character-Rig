from . import OP_open_addon_directory
from . import OP_file_open
from . import OP_image_pack
from . import OP_image_reload
from . import OP_rig_rename
from . import lib

modules = [
    OP_open_addon_directory,
    OP_file_open,
    OP_image_pack,
    OP_image_reload,
    OP_rig_rename,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()