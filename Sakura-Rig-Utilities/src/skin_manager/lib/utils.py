from pathlib import Path
import bpy

def allow_online():
    return bpy.app.online_access

def file_exists(path):
    return Path(path).exists()

def is_packed(file):
    try:
        return file.packed_files.values() != []
    except:
        return False

def lookup_name(bl_list: dict, query: str):
    for i, item in enumerate(bl_list):
        if query in item.name:
            return bl_list[i]
        else:
            continue
    return None
