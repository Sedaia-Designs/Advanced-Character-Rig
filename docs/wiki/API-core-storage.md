# `core.storage`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

Atomic JSON persistence helpers for extension-local data.

## `read_json`

```python
read_json(path: pathlib.Path) -> dict
```

Read a UTF-8 JSON file from disk.

## `write_json`

```python
write_json(path: pathlib.Path, data: dict) -> None
```

Atomically replace a UTF-8 JSON file with serialized data.
