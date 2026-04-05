# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Sedaia Minecraft Utilities.",
    "category": "Interface",
    "author": "Sakura Sedaia <sakusedaia@outlook.com>",
    "version": (4, 0, 0),
    "blender": (5, 0, 0),
    "location": "",
    "description": "",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "wiki_url": "",
}

import bpy
from bpy.app.handlers import persistent

from . import preferences
from . import operators
from . import rig_manager
from . import skin_manager
from . import sacr_uis

# Prefs must always be registered first
modules = [
    preferences,
    operators,
    rig_manager,
    skin_manager,
    sacr_uis,
]

@persistent
def refresh_rig_list_on_load(dummy):
    """Automatically refresh the rig list when a file is loaded."""
    def refresh():
        try:
            bpy.ops.sedaia_rigs_ot.refresh_rig_list()
        except Exception:
            pass
        return None
    try:
        # We use a timer to ensure the context is fully initialized
        bpy.app.timers.register(refresh, first_interval=0.1)
    except Exception:
        pass

@persistent
def refresh_skin_list_on_load(dummy):
    """Automatically refresh the rig list when a file is loaded."""
    def refresh():
        try:
            bpy.ops.sedaia_rigs_ot.refresh_skin_list()
        except Exception:
            pass
        return None
    try:
        # We use a timer to ensure the context is fully initialized
        bpy.app.timers.register(refresh, first_interval=0.1)
    except Exception:
        pass

def register():
    for m in modules:
        m.register()
    
    # Register the load handler
    if refresh_rig_list_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(refresh_rig_list_on_load)

    if refresh_skin_list_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(refresh_skin_list_on_load)
    # Also trigger once on registration (using a timer to avoid context issues)
    def initial_refresh():
        try:
            bpy.ops.sedaia_rigs_ot.refresh_rig_list()
        except Exception:
            pass
        try:
            bpy.ops.sedaia_rigs_ot.refresh_skin_list()
        except Exception:
            pass
        return None

    bpy.app.timers.register(initial_refresh, first_interval=0.5)

    # Register the manifest refresh timer
    bpy.app.timers.register(preferences.check_manifest_refresh, first_interval=1.0)

def unregister():
    # Unregister the load handler
    if refresh_rig_list_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(refresh_rig_list_on_load)

    if refresh_skin_list_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(refresh_skin_list_on_load)

    # Remove timers
    if bpy.app.timers.is_registered(preferences.check_manifest_refresh):
        bpy.app.timers.unregister(preferences.check_manifest_refresh)

    for m in reversed(modules):
        m.unregister()

if __name__ == "__main__":
    register()
