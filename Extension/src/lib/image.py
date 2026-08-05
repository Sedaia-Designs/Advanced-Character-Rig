import bpy


def is_packed(file):
    try:
        return file.packed_files.values() != []
    except:
        return False


def get_img(path):
    return bpy.data.images[path]
