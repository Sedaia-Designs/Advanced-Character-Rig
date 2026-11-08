"""Blender-free tests for `core.mojang`. No test opens a real connection.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import asyncio
import base64
import io
import json
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases.skins import SkinModel  # noqa: E402
from core.mojang import (  # noqa: E402
    MojangClient,
    MojangFormatError,
    MojangURL,
    PlayerNotFoundError,
    TextureRef,
    parse_profile,
)
from core.network import HTTPClient, NetworkError, NotFoundError  # noqa: E402

UUID = "069a79f444e94726a5befca90e38aaf5"
DASHED = "069a79f4-44e9-4726-a5be-fca90e38aaf5"
SKIN_HASH = "ae6c2d6b3a3f3bdbc93ee8c4bba6f3a0a1b7b1e9ec4a7b27a6e2c7d3d1f0e1a2"
CAPE_HASH = "953cac8b779fe41383e675ee2b86071a71658f2180f56fbce8aa315ea70e2ed6"


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int = 200):
        super().__init__(body)
        self.status = status


class FakeOpener:
    """Return a canned JSON body or HTTP error per URL, and record each URL."""

    def __init__(self, routes: dict[str, object]):
        self.routes = routes
        self.urls: list[str] = []

    def __call__(self, request, _timeout):
        url = request.full_url
        self.urls.append(url)
        result = self.routes[url]
        if isinstance(result, int):
            if result >= 400:
                raise HTTPError(url, result, "error", None, io.BytesIO())  # pyright: ignore[reportArgumentType]
            return FakeResponse(b"", status=result)
        return FakeResponse(json.dumps(result).encode())


def texture_url(texture_hash: str, host: str = "textures.minecraft.net") -> str:
    # Mojang really does send plain http texture URLs.
    return f"http://{host}/texture/{texture_hash}"


def session_body(textures: dict, name: str = "Notch", encoded: str | None = None) -> dict:
    payload = {"timestamp": 0, "profileId": UUID, "profileName": name, "textures": textures}
    value = encoded if encoded is not None else base64.b64encode(json.dumps(payload).encode()).decode()
    return {"id": UUID, "name": name, "properties": [{"name": "textures", "value": value}]}


def mojang(routes: dict[str, object]) -> tuple[MojangClient, FakeOpener]:
    opener = FakeOpener(routes)
    return MojangClient(HTTPClient().set_opener(opener)), opener


def run(coro):
    return asyncio.run(coro)


class LookupTests(unittest.TestCase):
    def test_returns_uuid_and_canonical_name(self):
        client, opener = mojang({MojangURL.PROFILES + "notch": {"id": UUID, "name": "Notch"}})
        self.assertEqual(run(client.lookup(" notch ")), (UUID, "Notch"))
        self.assertEqual(opener.urls, [MojangURL.PROFILES + "notch"])

    def test_unknown_name_raises_player_not_found(self):
        client, _ = mojang({MojangURL.PROFILES + "nobody": 404})
        with self.assertRaises(PlayerNotFoundError) as caught:
            run(client.lookup("nobody"))
        self.assertIsInstance(caught.exception, NotFoundError)

    def test_empty_name_raises_without_a_request(self):
        client, opener = mojang({})
        with self.assertRaises(PlayerNotFoundError):
            run(client.lookup("   "))
        self.assertEqual(opener.urls, [])

    def test_name_is_quoted_into_one_path_segment(self):
        url = MojangURL.PROFILES + "a%2F..%2Fb"
        client, opener = mojang({url: {"id": UUID, "name": "x"}})
        run(client.lookup("a/../b"))
        self.assertEqual(opener.urls, [url])

    def test_malformed_lookup_raises_format_error(self):
        for body in ({"name": "Notch"}, {"id": "not-a-uuid", "name": "Notch"}, [1, 2]):
            with self.subTest(body=body):
                client, _ = mojang({MojangURL.PROFILES + "notch": body})
                with self.assertRaises(MojangFormatError):
                    run(client.lookup("notch"))

    def test_server_error_stays_a_network_error(self):
        client, _ = mojang({MojangURL.PROFILES + "notch": 500})
        with self.assertRaises(NetworkError) as caught:
            run(client.lookup("notch"))
        self.assertNotIsInstance(caught.exception, PlayerNotFoundError)


class ProfileTests(unittest.TestCase):
    def profile(self, body):
        client, _ = mojang({MojangURL.SESSION + UUID: body})
        return run(client.profile(DASHED))

    def test_slim_skin_with_cape(self):
        profile = self.profile(
            session_body(
                {
                    "SKIN": {"url": texture_url(SKIN_HASH), "metadata": {"model": "slim"}},
                    "CAPE": {"url": texture_url(CAPE_HASH)},
                }
            )
        )
        self.assertEqual((profile.uuid, profile.name), (UUID, "Notch"))
        self.assertEqual(profile.skin, TextureRef(MojangURL.TEXTURES + SKIN_HASH, SKIN_HASH, SkinModel.SLIM))
        self.assertEqual(profile.cape, TextureRef(MojangURL.TEXTURES + CAPE_HASH, CAPE_HASH, None))

    def test_classic_skin_without_cape(self):
        profile = self.profile(session_body({"SKIN": {"url": texture_url(SKIN_HASH)}}))
        self.assertEqual(profile.skin.model, SkinModel.CLASSIC)
        self.assertIsNone(profile.cape)

    def test_texture_urls_are_rebuilt_as_https(self):
        profile = self.profile(session_body({"SKIN": {"url": texture_url(SKIN_HASH)}}))
        self.assertTrue(profile.skin.url.startswith("https://textures.minecraft.net/texture/"))

    def test_default_skin_has_no_texture(self):
        profile = self.profile(session_body({}))
        self.assertIsNone(profile.skin)
        self.assertIsNone(profile.cape)

    def test_unknown_uuid_raises_player_not_found(self):
        for status in (404, 204):
            with self.subTest(status=status):
                client, _ = mojang({MojangURL.SESSION + UUID: status})
                with self.assertRaises(PlayerNotFoundError):
                    run(client.profile(UUID))

    def test_invalid_uuid_argument_raises_value_error(self):
        client, opener = mojang({})
        with self.assertRaises(ValueError):
            run(client.profile("not-a-uuid"))
        self.assertEqual(opener.urls, [])


class MalformedProfileTests(unittest.TestCase):
    def assertFormatError(self, body):
        with self.assertRaises(MojangFormatError):
            parse_profile(body)

    def test_malformed_base64(self):
        self.assertFormatError(session_body({}, encoded="not base64!!"))

    def test_base64_that_is_not_json(self):
        self.assertFormatError(session_body({}, encoded=base64.b64encode(b"\xff\xfe").decode()))

    def test_missing_textures_property(self):
        self.assertFormatError({"id": UUID, "name": "Notch", "properties": []})

    def test_missing_fields(self):
        self.assertFormatError({"name": "Notch", "properties": []})
        self.assertFormatError({"id": UUID, "properties": []})
        self.assertFormatError("not an object")

    def test_foreign_texture_host(self):
        for url in (
            texture_url(SKIN_HASH, host="evil.example.com"),
            texture_url(SKIN_HASH, host="textures.minecraft.net.evil.example.com"),
            f"https://user@evil.example.com/texture/{SKIN_HASH}",
            f"file://textures.minecraft.net/texture/{SKIN_HASH}",
        ):
            with self.subTest(url=url):
                self.assertFormatError(session_body({"SKIN": {"url": url}}))

    def test_foreign_cape_host(self):
        body = session_body({"CAPE": {"url": texture_url(CAPE_HASH, host="evil.example.com")}})
        self.assertFormatError(body)

    def test_bad_texture_paths_and_hashes(self):
        for path in ("/texture/", "/texture/../etc", "/texture/abc/def", "/other/abc", "/texture/xyz"):
            with self.subTest(path=path):
                body = session_body({"SKIN": {"url": f"http://textures.minecraft.net{path}"}})
                self.assertFormatError(body)

    def test_unknown_skin_model(self):
        body = session_body({"SKIN": {"url": texture_url(SKIN_HASH), "metadata": {"model": "wide"}}})
        self.assertFormatError(body)


if __name__ == "__main__":
    unittest.main()
