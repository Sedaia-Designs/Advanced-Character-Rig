"""Mojang API adapter: turns username lookups and session profiles into project records.

Two endpoints are used:

- ``MojangURL.PROFILES + name`` returns ``{"id": uuid, "name": name}``.
- ``MojangURL.SESSION + uuid`` returns the profile, whose ``textures``
  property is base64-encoded JSON::

      {"textures": {"SKIN": {"url": "...", "metadata": {"model": "slim"}},
                    "CAPE": {"url": "..."}}}

Code past this module sees only `Profile` and `TextureRef`. Every malformed
response raises `MojangFormatError`, and an unknown player raises
`PlayerNotFoundError`. Network failures stay `NetworkError` from `core.network`.

Texture URLs come from a server response, so they are only accepted when their
host is `TEXTURE_HOST`. `HTTPClient` enforces HTTPS but not the host. Mojang
sends texture URLs as plain ``http://``, so an accepted URL is rebuilt from its
hash as ``MojangURL.TEXTURES + hash``, which is always HTTPS.

Patterns:

- Adapter: `parse_lookup` and `parse_profile` convert Mojang JSON into project
  records and errors.
- Facade: `MojangClient` gives the Skin Manager two task-shaped calls and hides
  the endpoints, base64, and JSON layout.
- Strategy: `MojangClient` takes an `HTTPClient`, so tests inject a fake opener.
"""

import base64
import binascii
import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import quote, urlsplit

from .databases.skins import SkinModel, normalize_uuid
from .network import HTTPClient, NotFoundError

# The only host texture URLs may point at. Texture URLs come from a server
# response, so they are checked against this before anything is downloaded.
TEXTURE_HOST = "textures.minecraft.net"

# Schemes accepted on texture URLs before they are rebuilt as HTTPS.
_TEXTURE_SCHEMES = frozenset({"http", "https"})
_TEXTURE_PATH = "/texture/"
_HEX = frozenset("0123456789abcdef")


class MojangURL(StrEnum):
    """Mojang endpoints. Append a username, UUID, or texture hash."""

    PROFILES = "https://api.mojang.com/users/profiles/minecraft/"
    SESSION = "https://sessionserver.mojang.com/session/minecraft/profile/"
    TEXTURES = f"https://{TEXTURE_HOST}/texture/"


class MojangFormatError(ValueError):
    """Raised when a Mojang response is missing fields, has the wrong types, or names a foreign host."""


class PlayerNotFoundError(NotFoundError):
    """Raised when Mojang has no player with the requested name or UUID."""


@dataclass(frozen=True, slots=True)
class TextureRef:
    """A skin or cape texture on `TEXTURE_HOST`.

    `url` is always ``MojangURL.TEXTURES + hash``. `model` is set for skins
    and `None` for capes.
    """

    url: str
    hash: str
    model: SkinModel | None


@dataclass(frozen=True, slots=True)
class Profile:
    """A player's current name and textures. `skin` is `None` for the default skin."""

    uuid: str
    name: str
    skin: TextureRef | None
    cape: TextureRef | None


# region Adapters


def _field(data: Any, key: str, kind: type, where: str) -> Any:
    """Return `data[key]` if `data` is a mapping and the value is a `kind`, else raise."""
    if not isinstance(data, Mapping):
        raise MojangFormatError(f"{where} is not a JSON object")
    value = data.get(key)
    if not isinstance(value, kind):
        raise MojangFormatError(f"{where} has no valid {key!r}")
    return value


def _uuid(value: str, where: str) -> str:
    try:
        return normalize_uuid(value)
    except ValueError as error:
        raise MojangFormatError(f"{where} has an invalid UUID") from error


def parse_lookup(data: Any) -> tuple[str, str]:
    """Return ``(uuid, name)`` from a ``MojangURL.PROFILES`` response."""
    where = "Username lookup"
    uuid = _uuid(_field(data, "id", str, where), where)
    name = _field(data, "name", str, where)
    return uuid, name


def parse_texture(entry: Any, model: SkinModel | None) -> TextureRef:
    """Return a `TextureRef` from a ``SKIN`` or ``CAPE`` entry, checking its host."""
    where = "Texture entry"
    parts = urlsplit(_field(entry, "url", str, where))
    if parts.scheme not in _TEXTURE_SCHEMES or parts.hostname != TEXTURE_HOST:
        raise MojangFormatError(f"Texture URL is not on {TEXTURE_HOST}")
    if not parts.path.startswith(_TEXTURE_PATH) or parts.query or parts.fragment:
        raise MojangFormatError("Texture URL has an unexpected path")

    # The hash is the last path segment. It later names files on disk, so it
    # must be plain hex: no separators, dots, or empty strings.
    texture_hash = parts.path.removeprefix(_TEXTURE_PATH).lower()
    if not texture_hash or not set(texture_hash) <= _HEX:
        raise MojangFormatError("Texture URL has an invalid hash")
    return TextureRef(MojangURL.TEXTURES + texture_hash, texture_hash, model)


def _skin_model(entry: Mapping[str, Any]) -> SkinModel:
    """Return the skin's model. Mojang omits ``metadata`` for classic skins."""
    metadata = entry.get("metadata")
    if metadata is None:
        return SkinModel.CLASSIC
    if not isinstance(metadata, Mapping):
        raise MojangFormatError("Skin metadata is not a JSON object")
    model = metadata.get("model", SkinModel.CLASSIC)
    try:
        return SkinModel(model)
    except ValueError as error:
        raise MojangFormatError(f"Unknown skin model {model!r}") from error


def _decode_textures(properties: list[Any]) -> Mapping[str, Any]:
    """Find the ``textures`` property and return its decoded ``textures`` object."""
    value = next(
        (p.get("value") for p in properties if isinstance(p, Mapping) and p.get("name") == "textures"),
        None,
    )
    if not isinstance(value, str):
        raise MojangFormatError("Profile has no textures property")
    try:
        decoded = json.loads(base64.b64decode(value, validate=True))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MojangFormatError("Profile textures are not valid base64 JSON") from error
    return _field(decoded, "textures", Mapping, "Profile textures")


def parse_profile(data: Any) -> Profile:
    """Return a `Profile` from a ``MojangURL.SESSION`` response."""
    where = "Session profile"
    uuid = _uuid(_field(data, "id", str, where), where)
    name = _field(data, "name", str, where)
    textures = _decode_textures(_field(data, "properties", list, where))

    skin_entry = textures.get("SKIN")
    cape_entry = textures.get("CAPE")
    skin = None
    if skin_entry is not None:
        if not isinstance(skin_entry, Mapping):
            raise MojangFormatError("Skin entry is not a JSON object")
        skin = parse_texture(skin_entry, _skin_model(skin_entry))
    cape = parse_texture(cape_entry, None) if cape_entry is not None else None
    return Profile(uuid, name, skin, cape)


# endregion


class MojangClient:
    """Look up players and their textures through Mojang's public API.

    ``MojangClient(HTTPClient())`` is ready to use. Pass a configured
    `HTTPClient` to change the timeout or, in tests, the opener.
    """

    def __init__(self, http: HTTPClient):
        self.http = http

    async def lookup(self, name: str) -> tuple[str, str]:
        """Return ``(uuid, name)`` for `name`, with the name in Mojang's capitalisation.

        Raises `PlayerNotFoundError` if no player has that name,
        `MojangFormatError` for a malformed response, and `NetworkError` for
        any other request failure.
        """
        name = name.strip()
        if not name:
            raise PlayerNotFoundError("No username given")
        try:
            data = await self.http.fetch_json(MojangURL.PROFILES + quote(name, safe=""))
        except NotFoundError as error:
            raise PlayerNotFoundError(f"No Minecraft player is named {name!r}") from error
        return parse_lookup(data)

    async def profile(self, uuid: str) -> Profile:
        """Return the current `Profile` for `uuid`, dashed or not.

        Raises `ValueError` for a malformed `uuid`, and otherwise the same
        errors as `lookup`.
        """
        uuid = normalize_uuid(uuid)
        try:
            data = await self.http.fetch_json(MojangURL.SESSION + uuid)
        except NotFoundError as error:
            raise PlayerNotFoundError(f"No Minecraft player has UUID {uuid}") from error
        return parse_profile(data)
