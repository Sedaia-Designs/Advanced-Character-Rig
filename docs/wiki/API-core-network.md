# `core.network`

[Home](https://github.com/Sedaia-Designs/Advanced-Character-Rig/wiki/Home)

Small timeout-bound HTTP helpers for extension services.

## `NetworkError`

Unspecified run-time error.

## `get_json`

```python
get_json(url: str, *, timeout: int) -> dict
```

Fetch and decode a JSON object, raising NetworkError on transport or decode failure.

## `download_file`

```python
download_file(url: str, destination: pathlib.Path, *, timeout: int) -> None
```

Download response bytes to destination within the requested timeout.
