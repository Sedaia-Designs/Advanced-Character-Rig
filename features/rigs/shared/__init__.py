"""Shared operators for all supported SACR rig revisions."""

from bpy.utils import register_class, unregister_class

from .image_tools import IMAGE_pack, IMAGE_reload
from .operators import FILE_open, RIGS_set_name
from ....core.ids import ID


OPS = {
    "file_open": ID("file_open").operator_for("UTIL"),
    "image_pack": ID("image_pack").operator_for("UTIL"),
    "image_reload": ID("image_reload").operator_for("UTIL"),
    "rig_rename": ID("rig_rename").operator_for("UTIL"),
}
classes = (FILE_open, IMAGE_pack, IMAGE_reload, RIGS_set_name)


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)
