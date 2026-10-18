# `core.network`

Small timeout-bound HTTP helpers for extension services.

## `NetworkError`

Unspecified run-time error.

## `get_json(url: str, *, timeout: int) -> dict`

Fetch and decode a JSON object, raising NetworkError on transport or decode failure.

## `download_file(url: str, destination: pathlib.Path, *, timeout: int) -> None`

Download response bytes to destination within the requested timeout.
