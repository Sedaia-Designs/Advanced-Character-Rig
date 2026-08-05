import bpy
import bpy.utils as U
from importlib import reload

bl_info = {
    "name": "SACR R7.5 UI",
    "author": "Sakura Sedaia <sakusedaia@outlook.com>",
    "category": "Interface",
    "version": (3, 0, 0),
    "blender": (5, 1, 0),
    "location": "View 3D > Tool Window (N) > SACR R7.5",
}

#
# Here is a list of features changed when the rig is set to Lite
# - Long hair Rig Removed
# - Eyelashes Removed
# - Body Lattices Removed
# - Eyesparkles
#


# Helper Functions


if "PT_Main" in locals():
    reload(PT_Main)
else:
    from . import PT_Main

if "PT_Face" in locals():
    reload(PT_Face)
else:
    from . import PT_Face

if "PT_Collections" in locals():
    reload(PT_Collections)
else:
    from . import PT_Collections

modules = [PT_Main, PT_Face, PT_Collections]


def register():
    for m in modules:
        m.register()


def unregister():
    for m in reversed(modules):
        m.unregister()


if __name__ == "__main__":
    register()
