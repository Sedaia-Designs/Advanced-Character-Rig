"""Network and storage workflow for Minecraft player skins."""

from base64 import b64decode
import json
from pathlib import Path
from ...core.network import NetworkError, download_file, get_json

from .constants import MOJANG_URLS, REQUEST_TIMEOUT_SECONDS
from .models import RemotePlayer, RemoteTexture


class SkinServiceError(RuntimeError):
    pass


def _json_from_url(url: str) -> dict:
    try:
        return get_json(url, timeout=REQUEST_TIMEOUT_SECONDS)
    except NetworkError as exc:
        raise SkinServiceError("The Minecraft service did not return valid data.") from exc


def _texture(value: dict | None) -> RemoteTexture:
    if not value:
        return RemoteTexture(url="", texture_hash="", exists=False)
    url = value["url"]
    return RemoteTexture(url=url, texture_hash=url.rsplit("/", 1)[-1])


def skin_data_is_slim(skin_data: dict) -> bool:
    return skin_data.get("metadata", {}).get("model") == "slim"


def fetch_player(username: str) -> RemotePlayer:
    profile = _json_from_url(f"{MOJANG_URLS['api']}{username}")
    try:
        session = _json_from_url(f"{MOJANG_URLS['profile']}{profile['id']}")
        encoded = session["properties"][0]["value"]
        textures = json.loads(b64decode(encoded).decode("utf-8"))["textures"]
        skin = _texture(textures["SKIN"])
    except (KeyError, IndexError, ValueError, UnicodeDecodeError) as exc:
        raise SkinServiceError("The Minecraft profile is missing skin data.") from exc
    model = "1" if skin_data_is_slim(textures["SKIN"]) else "0"
    return RemotePlayer(profile["id"], profile.get("name", username), model, skin, _texture(textures.get("CAPE")))


def download(url: str, destination: Path) -> None:
    try:
        download_file(url, destination, timeout=REQUEST_TIMEOUT_SECONDS)
    except NetworkError as exc:
        raise SkinServiceError("The skin texture could not be downloaded.") from exc


def download_player_textures(root: Path, username: str, player: RemotePlayer, index: int) -> dict:
    directory = root / username
    directory.mkdir(parents=True, exist_ok=True)
    suffix = "" if index == 0 else f"_{index}"
    skin_path = directory / f"{username}_Skin{suffix}.png"
    download(player.skin.url, skin_path)
    cape_path = ""
    if player.cape.exists:
        cape_path = str(directory / f"{username}_Cape{suffix}.png")
        download(player.cape.url, Path(cape_path))
    return {
        "skin": {"index": index, "path": str(skin_path), "hash": player.skin.texture_hash, "model": player.model},
        "cape": {"index": index, "path": cape_path, "hash": player.cape.texture_hash, "exists": player.cape.exists},
    }
