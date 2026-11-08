"""Registration layer for the Skin Manager operators.

Also registers a ``load_pre`` handler: loading a file ends modal operators,
but a background sync's worker thread keeps running, so the handler cancels it
and clears the sync state before the new file opens.
"""

import bpy
from bpy.app.handlers import persistent
from bpy.utils import register_class, unregister_class

from ....core.skin_manager import sync_progress
from .add import classes as add_classes
from .import_legacy import classes as import_legacy_classes
from .load import classes as load_classes
from .purge import classes as purge_classes
from .router import classes as router_classes

classes = (
    *load_classes,
    *add_classes,
    *purge_classes,
    *router_classes,
    *import_legacy_classes,
)


def stop_sync() -> None:
    """Cancel a running background sync, if any, and forget it."""
    sync_progress.cancel()
    sync_progress.reset()


@persistent
def stop_sync_on_load(*_args) -> None:
    """``load_pre`` handler: nothing from a running sync is applied to the next file."""
    stop_sync()


def register():
    """Register this module's Blender classes and the file-load handler."""
    for cls in classes:
        register_class(cls)
    bpy.app.handlers.load_pre.append(stop_sync_on_load)


def unregister():
    """Stop a running sync, remove the handler, and unregister this module's Blender classes."""
    stop_sync()
    if stop_sync_on_load in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(stop_sync_on_load)
    for cls in reversed(classes):
        unregister_class(cls)
