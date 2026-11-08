"""Blender-free tests for `core.network`. No test opens a real connection.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import asyncio
import io
import sys
import tempfile
import unittest
from email.message import Message
from pathlib import Path
from unittest import mock
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import network  # noqa: E402
from core.network import DEFAULT_USER_AGENT, HTTPClient, NetworkError, NotFoundError  # noqa: E402

URL = "https://example.com/private/path?token=secret"


class FakeResponse(io.BytesIO):
    """A stand-in for `http.client.HTTPResponse` with a status and a body."""

    def __init__(self, body: bytes = b"", status: int = 200):
        super().__init__(body)
        self.status = status


class FailingResponse(FakeResponse):
    """A response whose connection drops after the first chunk."""

    def read(self, size=-1):
        if self.tell():
            raise TimeoutError("read timed out")
        return super().read(size)


class FakeOpener:
    """Record each request and return `response` or raise `error`."""

    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        if self.error is not None:
            raise self.error
        return self.response


def client(response=None, error=None) -> tuple[HTTPClient, FakeOpener]:
    opener = FakeOpener(response, error)
    return HTTPClient().set_opener(opener), opener


class BuilderTests(unittest.TestCase):
    def test_defaults(self):
        c = HTTPClient()
        self.assertEqual(c.user_agent, DEFAULT_USER_AGENT)
        self.assertIs(c.opener, network.urlopen_opener)
        self.assertGreater(c.timeout, 0)

    def test_setters_chain_and_return_the_client(self):
        c = HTTPClient()
        result = (
            c.set_user_agent("Test/1")
            .set_timeout(3)
            .set_max_json_bytes(10)
            .set_max_download_bytes(20)
            .set_chunk_size(5)
        )
        self.assertIs(result, c)
        self.assertEqual(
            (c.user_agent, c.timeout, c.max_json_bytes, c.max_download_bytes, c.chunk_size),
            ("Test/1", 3, 10, 20, 5),
        )

    def test_clients_do_not_share_options(self):
        a = HTTPClient().set_timeout(1)
        self.assertNotEqual(HTTPClient().timeout, a.timeout)

    def test_rejects_invalid_options(self):
        c = HTTPClient()
        for setter, value in (
            (c.set_timeout, 0),
            (c.set_max_json_bytes, -1),
            (c.set_max_download_bytes, 0),
            (c.set_chunk_size, 0),
            (c.set_user_agent, ""),
        ):
            with self.subTest(setter=setter.__name__), self.assertRaises(ValueError):
                setter(value)


class UrlopenOpenerTests(unittest.TestCase):
    def test_passes_timeout_by_keyword(self):
        # A positional second argument would be `urlopen`'s `data`, turning
        # the request into a POST with no timeout.
        request = network.Request(URL)
        with mock.patch.object(network, "urlopen") as fake:
            network.urlopen_opener(request, 4.0)
        fake.assert_called_once_with(request, timeout=4.0)
        self.assertEqual(request.get_method(), "GET")


class FetchJsonTests(unittest.TestCase):
    def test_returns_decoded_json(self):
        c, _ = client(FakeResponse(b'{"id": "abc"}'))
        self.assertEqual(asyncio.run(c.fetch_json(URL)), {"id": "abc"})

    def test_sends_configured_timeout_and_user_agent(self):
        c, opener = client(FakeResponse(b"{}"))
        asyncio.run(c.set_timeout(3.0).set_user_agent("Test/1").fetch_json(URL))
        request, timeout = opener.calls[0]
        self.assertEqual(timeout, 3.0)
        self.assertEqual(request.get_header("User-agent"), "Test/1")

    def test_runs_requests_concurrently(self):
        c = HTTPClient().set_opener(lambda request, timeout: FakeResponse(b"[1]"))

        async def both():
            return await asyncio.gather(c.fetch_json(URL), c.fetch_json(URL))

        self.assertEqual(asyncio.run(both()), [[1], [1]])

    def test_rejects_non_https(self):
        for url in ("http://example.com/", "file:///etc/passwd", "ftp://example.com/"):
            c, opener = client(FakeResponse(b"{}"))
            with self.subTest(url=url), self.assertRaises(NetworkError):
                asyncio.run(c.fetch_json(url))
            self.assertEqual(opener.calls, [])

    def test_no_content_is_not_found(self):
        c, _ = client(FakeResponse(status=204))
        with self.assertRaises(NotFoundError):
            asyncio.run(c.fetch_json(URL))

    def test_http_404_is_not_found(self):
        c, _ = client(error=HTTPError(URL, 404, "Not Found", Message(), None))
        with self.assertRaises(NotFoundError):
            asyncio.run(c.fetch_json(URL))

    def test_other_http_error_is_network_error(self):
        c, _ = client(error=HTTPError(URL, 503, "Unavailable", Message(), None))
        with self.assertRaises(NetworkError) as caught:
            asyncio.run(c.fetch_json(URL))
        self.assertNotIsInstance(caught.exception, NotFoundError)

    def test_connection_errors_become_network_error(self):
        for error in (URLError("no route"), TimeoutError(), ConnectionResetError()):
            c, _ = client(error=error)
            with self.subTest(error=error), self.assertRaises(NetworkError):
                asyncio.run(c.fetch_json(URL))

    def test_invalid_json(self):
        c, _ = client(FakeResponse(b"<html>"))
        with self.assertRaises(NetworkError):
            asyncio.run(c.fetch_json(URL))

    def test_oversized_body(self):
        c, _ = client(FakeResponse(b"[1, 2, 3]"))
        with self.assertRaises(NetworkError):
            asyncio.run(c.set_max_json_bytes(4).fetch_json(URL))

    def test_errors_never_include_the_full_url(self):
        c, _ = client(error=URLError("no route"))
        with self.assertRaises(NetworkError) as caught:
            asyncio.run(c.fetch_json(URL))
        message = str(caught.exception)
        self.assertIn("example.com", message)
        self.assertNotIn("secret", message)
        self.assertNotIn("/private", message)


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / "player" / "skin.png"

    def leftovers(self):
        return [p for p in self.dest.parent.iterdir() if p.name.endswith(".part")]

    def test_writes_file_and_creates_folder(self):
        c, _ = client(FakeResponse(b"png-bytes"))
        asyncio.run(c.download(URL, self.dest))
        self.assertEqual(self.dest.read_bytes(), b"png-bytes")
        self.assertEqual(self.leftovers(), [])

    def test_rejected_url_touches_nothing(self):
        c, _ = client(FakeResponse(b"png"))
        with self.assertRaises(NetworkError):
            asyncio.run(c.download("http://example.com/skin.png", self.dest))
        self.assertFalse(self.dest.parent.exists())

    def test_failed_download_keeps_existing_file(self):
        self.dest.parent.mkdir(parents=True)
        self.dest.write_bytes(b"old")
        c, _ = client(FailingResponse(b"new-bytes"))
        with self.assertRaises(NetworkError):
            asyncio.run(c.set_chunk_size(2).download(URL, self.dest))
        self.assertEqual(self.dest.read_bytes(), b"old")
        self.assertEqual(self.leftovers(), [])

    def test_bad_status_leaves_no_file(self):
        c, _ = client(FakeResponse(status=204))
        with self.assertRaises(NotFoundError):
            asyncio.run(c.download(URL, self.dest))
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.leftovers(), [])

    def test_oversized_download_leaves_no_file(self):
        c, _ = client(FakeResponse(b"too-large"))
        with self.assertRaises(NetworkError):
            asyncio.run(c.set_max_download_bytes(4).download(URL, self.dest))
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.leftovers(), [])

    def test_disk_errors_are_not_network_errors(self):
        c, _ = client(FakeResponse(b"png"))
        with mock.patch.object(network.os, "replace", side_effect=PermissionError):
            with self.assertRaises(PermissionError):
                asyncio.run(c.download(URL, self.dest))
        self.assertEqual(self.leftovers(), [])


if __name__ == "__main__":
    unittest.main()
