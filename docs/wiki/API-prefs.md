# `prefs`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

## `PREFS_user_preferences`

### `bl_idname`

### `prompt_to_refresh_player_data`

### `draw`

```python
draw(self, context)
```

Draw this UI element for the current Blender context.

## `get_prefs`

```python
get_prefs(context: __main__.Context | None = None) -> __main__.Preferences | None
```

Intermediate method for grabbing preferences

## `PREFS_file_open`

### `bl_label`

### `bl_idname`

### `path`

### `execute`

```python
execute(self, context)
```

Apply this operator to the current Blender context.

## `register`

```python
register()
```

Register this module's Blender classes.

## `unregister`

```python
unregister()
```

Unregister this module's Blender classes.
