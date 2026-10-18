"""Small value objects for Mojang skin metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RemoteTexture:
    url: str
    texture_hash: str
    exists: bool = True


@dataclass(frozen=True)
class RemotePlayer:
    uuid: str
    name: str
    model: str
    skin: RemoteTexture
    cape: RemoteTexture


@dataclass(frozen=True)
class SkinEntry:
    index: int
    path: str
    texture_hash: str
    model: str


@dataclass(frozen=True)
class CapeEntry:
    index: int
    path: str
    texture_hash: str
    exists: bool


@dataclass(frozen=True)
class PlayerData:
    uuid: str
    name: str
    skins: tuple[SkinEntry, ...]
    capes: tuple[CapeEntry, ...]
