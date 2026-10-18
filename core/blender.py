"""Narrow helpers for safe access to Blender data."""

import bpy


def online_access_enabled() -> bool:
    return bpy.app.online_access


def is_packed(image) -> bool:
    return bool(getattr(image, "packed_file", None) or getattr(image, "packed_files", None))


def find_named(items, query: str):
    return next((item for item in items if query in item.name), None)
