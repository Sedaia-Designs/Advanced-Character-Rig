# `core.blender`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

Narrow helpers for safe access to Blender data.

## `online_access_enabled`

```python
online_access_enabled() -> bool
```

Return Blender's current Online Access preference.

## `is_packed`

```python
is_packed(image) -> bool
```

Return whether an image has one or more packed files.

## `find_named`

```python
find_named(items, query: str)
```

Find the first item whose name contains query, if one exists.
