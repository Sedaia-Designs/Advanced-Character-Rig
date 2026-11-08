"""Async HTTPS requests for JSON lookups and file downloads.

The standard library has no async HTTP client, so each request runs the
blocking `urllib` call in a worker thread through `asyncio.to_thread`. Python
releases the GIL while it waits on the socket, so several requests started with
`asyncio.gather` really do run at the same time.

This module never checks Blender's Online Access setting. The calling operator
must check `bpy.app.online_access` before it starts any request here.

Errors name only the host, never the full URL, so a private asset URL is never
printed or shown in a report.

Patterns:

- Builder: `HTTPClient` collects request options through chained setters.
- Strategy: the `Opener` that sends each request is swappable, so tests never
  touch the network.
- Adapter: `urlopen_opener` fits `urllib.request.urlopen` to the `Opener`
  interface, and `_request_error` converts `urllib` and socket errors into
  `NetworkError`.
"""

import asyncio
import json
import os
import tempfile
from collections.abc import Callable, Iterator
from http import HTTPStatus
from pathlib import Path
from typing import Any, Protocol, Self
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT = "SakuraCharacterRig"

class Response(Protocol):
    """The parts of `http.client.HTTPResponse` that `HTTPClient` uses."""

    status: int

    def read(self, size: int = -1, /) -> bytes: ...

    def close(self) -> None: ...

    def __enter__(self) -> Any: ...

    def __exit__(self, *exc_info: object) -> Any: ...


# Strategy that sends a request: takes the request and a timeout in seconds and
# returns an open `Response`. `urlopen_opener` is the default. Tests pass a fake.
Opener = Callable[[Request, float], Response]


def urlopen_opener(request: Request, timeout: float) -> Response:
    """Open `request` with `urllib.request.urlopen`, adapted to the `Opener` interface.

    `urlopen`'s second positional parameter is `data`, not `timeout`, so it
    cannot be the opener directly: it would send every request as a POST with
    the timeout as its body, and never time out.
    """
    return urlopen(request, timeout=timeout)


class NetworkError(Exception):
    """Raised when a request fails, times out, or returns an invalid response."""


class NotFoundError(NetworkError):
    """Raised when the server has nothing at the requested URL (HTTP 404 or 204)."""


def _host(url: str) -> str:
    """Return the host of `url`, which is safe to put in error messages."""
    return urlsplit(url).netloc or "<unknown host>"


def _request_error(url: str, error: OSError) -> NetworkError:
    """Convert a `urllib` or socket error into a `NetworkError` that names only the host."""
    if isinstance(error, HTTPError):
        # An HTTPError holds the open response; close it so the socket is not
        # left for the garbage collector.
        error.close()
        if error.code == HTTPStatus.NOT_FOUND:
            return NotFoundError(f"Nothing found at {_host(url)} (HTTP 404)")
        return NetworkError(f"{_host(url)} answered with HTTP {error.code}")
    if isinstance(error, TimeoutError):
        return NetworkError(f"Request to {_host(url)} timed out")
    if isinstance(error, URLError):
        return NetworkError(f"Could not reach {_host(url)}: {error.reason}")
    return NetworkError(f"Connection to {_host(url)} failed: {error}")


def _positive(name: str, value: float) -> None:
    """Raise `ValueError` unless `value` is greater than zero."""
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero, got {value}")


class HTTPClient:
    """
    Factory for HTTPS requests that share one set of request options.

    Every option starts at a working default, so ``HTTPClient()`` is ready to
    use. Change an option with its setter. Each setter returns the client, so
    calls can be chained::

        client = HTTPClient().set_user_agent("SakuraCharacterRig/7.5.0").set_timeout(5)
        profile = await client.fetch_json(url)

    Only HTTPS URLs are accepted. ``urlopen`` would also open ``file:``,
    ``ftp:``, and plain ``http:`` URLs, so a URL taken from a server response
    or a user field could otherwise read local files.
    """

    def __init__(self):
        self.user_agent: str = DEFAULT_USER_AGENT
        self.timeout: float = 10.0
        self.max_json_bytes: int = 1 * 1024 * 1024
        self.max_download_bytes: int = 16 * 1024 * 1024
        self.chunk_size: int = 64 * 1024
        self.opener: Opener = urlopen_opener

    def set_user_agent(self, user_agent: str) -> Self:
        """
        Set the ``User-Agent`` header sent with every request.
        """
        if not user_agent:
            raise ValueError("user_agent must be a non-empty string")
        self.user_agent = user_agent
        return self

    def set_timeout(self, timeout: float) -> Self:
        """
        Set how many seconds to wait for the connection or for each read before failing.

        This limits each blocking socket operation, not the whole request, so a
        slow download that keeps receiving data does not time out.
        """
        _positive("timeout", timeout)
        self.timeout = timeout
        return self

    def set_max_json_bytes(self, max_json_bytes: int) -> Self:
        """
        Set the largest JSON body ``fetch_json`` accepts before failing.
        """
        _positive("max_json_bytes", max_json_bytes)
        self.max_json_bytes = max_json_bytes
        return self

    def set_max_download_bytes(self, max_download_bytes: int) -> Self:
        """
        Set the largest file ``download`` accepts before failing.
        """
        _positive("max_download_bytes", max_download_bytes)
        self.max_download_bytes = max_download_bytes
        return self

    def set_chunk_size(self, chunk_size: int) -> Self:
        """
        Set how many bytes are read from the connection at a time.
        """
        _positive("chunk_size", chunk_size)
        self.chunk_size = chunk_size
        return self

    def set_opener(self, opener: Opener) -> Self:
        """
        Set the function that opens requests. See ``Opener``. Tests use this to avoid the network.
        """
        self.opener = opener
        return self

    async def fetch_json(self, url: str) -> Any:
        """
        Fetch ``url`` and return its decoded JSON body.

        Raises ``NotFoundError`` for HTTP 404 or 204, and ``NetworkError`` for
        any other failure: a non-HTTPS URL, a timeout, a connection error,
        another status code, a body over ``max_json_bytes``, or invalid JSON.
        """
        return await asyncio.to_thread(self._fetch_json_blocking, url)

    async def download(self, url: str, dest: Path) -> None:
        """
        Download ``url`` to ``dest``, replacing it atomically.

        Creates the parent folder if needed. If anything fails, the existing
        file at ``dest``, if any, is left untouched and no partial file remains.

        Raises the same errors as ``fetch_json``, except that the size limit
        is ``max_download_bytes`` and the body is not decoded. File system
        errors while writing ``dest`` are raised unchanged as ``OSError``.
        """
        await asyncio.to_thread(self._download_blocking, url, dest)

    def _request(self, url: str, accept: str) -> Request:
        """Return a GET request for `url`, refusing anything that is not HTTPS."""
        if urlsplit(url).scheme != "https":
            raise NetworkError(f"Refusing a non-HTTPS request to {_host(url)}")
        return Request(url, headers={"Accept": accept, "User-Agent": self.user_agent})

    def _open(self, request: Request, url: str):
        """Open `request`, convert connection errors, and raise unless the status is 200."""
        try:
            response = self.opener(request, self.timeout)
        except OSError as error:  # URLError, HTTPError, and TimeoutError are all OSError.
            raise _request_error(url, error) from error

        status = response.status
        if status == HTTPStatus.OK:
            return response
        response.close()
        if status in (HTTPStatus.NOT_FOUND, HTTPStatus.NO_CONTENT):
            raise NotFoundError(f"Nothing found at {_host(url)} (HTTP {status})")
        raise NetworkError(f"{_host(url)} answered with HTTP {status}")

    def _read(self, response, url: str, limit: int) -> Iterator[bytes]:
        """Yield the response body in chunks, raising once it grows past `limit` bytes.

        Only errors from reading the socket become `NetworkError`, so a caller
        writing each chunk to disk still sees its own `OSError` unchanged.
        """
        total = 0
        while True:
            try:
                chunk = response.read(self.chunk_size)
            except OSError as error:
                raise _request_error(url, error) from error
            if not chunk:
                return
            total += len(chunk)
            if total > limit:
                raise NetworkError(f"Response from {_host(url)} is larger than {limit} bytes")
            yield chunk

    def _fetch_json_blocking(self, url: str) -> Any:
        request = self._request(url, "application/json")
        with self._open(request, url) as response:
            body = b"".join(self._read(response, url, self.max_json_bytes))
        try:
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise NetworkError(f"{_host(url)} did not return valid JSON") from error

    def _download_blocking(self, url: str, dest: Path) -> None:
        request = self._request(url, "*/*")  # Refuse a bad URL before touching the disk.
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Write next to `dest` and swap it in only once the whole body has
        # arrived, so an interrupted download never replaces a good file.
        fd, temp_name = tempfile.mkstemp(dir=dest.parent, prefix=f".{dest.name}.", suffix=".part")
        temp_path = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as file, self._open(request, url) as response:
                for chunk in self._read(response, url, self.max_download_bytes):
                    file.write(chunk)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_path, dest)
        except BaseException:
            temp_path.unlink(missing_ok=True)
            raise
