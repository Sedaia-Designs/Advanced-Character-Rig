"""Small timeout-bound HTTP helpers for extension services."""

import json
from pathlib import Path
from urllib import error, request


class NetworkError(RuntimeError):
    pass


def get_json(url: str, *, timeout: int) -> dict:
    try:
        with request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read())
    except (error.HTTPError, error.URLError, json.JSONDecodeError) as exc:
        raise NetworkError("The remote service did not return valid data.") from exc


def download_file(url: str, destination: Path, *, timeout: int) -> None:
    try:
        with request.urlopen(url, timeout=timeout) as response:
            destination.write_bytes(response.read())
    except (error.HTTPError, error.URLError) as exc:
        raise NetworkError("The remote file could not be downloaded.") from exc
