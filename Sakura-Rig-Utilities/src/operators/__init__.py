from . import OP_open_addon_directory
from . import OP_file_open
from . import OP_open_url
from . import OP_image_pack
from . import OP_image_reload
from . import OP_rig_rename
from . import OP_copy_debug_info
from . import OP_enable_online_access
from . import lib

modules = [
    OP_open_addon_directory,
    OP_file_open,
    OP_open_url,
    OP_image_pack,
    OP_image_reload,
    OP_rig_rename,
    OP_copy_debug_info,
    OP_enable_online_access,
]

def register():
    for m in modules:
        m.register()

def unregister():
    for m in reversed(modules):
        m.unregister()