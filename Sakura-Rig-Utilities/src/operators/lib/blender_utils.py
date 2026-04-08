import bpy
from pathlib import Path

def allow_online():
    """Check if Blender allows online access."""
    return bpy.app.online_access

def is_packed(file):
    """Check if a Blender file (or data-block) has packed files."""
    try:
        return file.packed_files.values() != []
    except (AttributeError, Exception):
        return False

def lookup_name(bl_list, query: str):
    """
    Search for a string within the 'name' property of items in a Blender collection.
    Returns the first matching item or None.
    """
    for item in bl_list:
        if query in item.name:
            return item
    return None

def get_addon_directory():
    """Returns the root directory of the addon."""
    from ...preferences import get_preferences
    return Path(get_preferences().addon_directory)
