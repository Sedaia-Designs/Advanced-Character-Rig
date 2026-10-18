# `core.blender`

Narrow helpers for safe access to Blender data.

## `online_access_enabled() -> bool`

Return Blender's current Online Access preference.

## `is_packed(image) -> bool`

Return whether an image has one or more packed files.

## `find_named(items, query: str)`

Find the first item whose name contains query, if one exists.
