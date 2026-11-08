"""Skin Manager workflow shared by every Skin Manager operator.

`SkinManager` ties together the skin tables (`SkinDatabase`), Mojang
(`MojangClient`), and the player data folder. Operators build one with the
paths and database session Blender gives them, call one method, and apply the
result to the rig.

Texture files are named by their hash, under one folder per player UUID::

    <player data>/<uuid>/skin_<hash>.png
    <player data>/<uuid>/cape_<hash>.png

so a texture that is already stored is never downloaded again, files never
overwrite each other, and a renamed player keeps their history. Paths are
stored relative to the player data folder. Legacy imports keep their absolute
paths, which resolve unchanged.

Nothing here is specific to one rig. Rig names and values come from the
active rig's `core.skin_targets.SkinTarget`.

Patterns:

- Facade: `SkinManager` gives operators task-shaped calls (`sync`,
  `selection`, `purge`, `import_legacy_dir`) and hides SQL, HTTP, and files.
- Strategy: the database session factory, the `MojangClient`, and `sync`'s
  `should_cancel` check are injected, so tests use in-memory SQLite, a fake
  client, and a scripted cancel.
- Observer: `subscribe` registers callbacks that `sync` notifies at each
  `SyncStage`, so the Blender layer can report progress without core
  importing it.
- Singleton: `sync_progress` records the one background sync allowed at a time.
"""

import json
import shutil
import sqlite3
from collections.abc import Callable, Generator, Iterable
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .databases.skins import (
    Cape,
    LegacyFormatError,
    Player,
    Skin,
    SkinDatabase,
    SkinModel,
    normalize_uuid,
)
from .background import BackgroundTask
from .mojang import MojangClient, TextureRef

# Glob, relative to a legacy player data folder, that finds legacy player files.
LEGACY_GLOB = "*/*_Data.json"

# Opens a database session for a `with` block that commits on success and
# rolls back on error, such as `preferences.access.db_session`.
SessionFactory = Callable[[], AbstractContextManager[sqlite3.Connection]]

# Observer callback: receives the stage and the player name being synced.
SyncListener = Callable[["SyncStage", str], None]

# Strategy that `sync` asks at each checkpoint whether to stop, such as
# `BackgroundTask.cancelled`.
CancelCheck = Callable[[], bool]


class Route(StrEnum):
    """What the Skin Manager router does with the username on the rig."""

    LOAD = "load"  # Stored locally and offline or no prompt: apply the newest stored skin.
    PROMPT = "prompt"  # Stored locally and online: ask whether to load, check for new, or purge.
    DOWNLOAD = "download"  # Not stored yet and online: download and apply.
    OFFLINE_ERROR = "offline_error"  # Not stored yet and offline: nothing can be done.


class SyncStage(StrEnum):
    """Progress points `SkinManager.sync` publishes to its subscribers, in order."""

    LOOKUP = "lookup"  # Looking up the username.
    PROFILE = "profile"  # Fetching the profile and its texture URLs.
    DOWNLOAD_SKIN = "download_skin"  # Downloading a skin that is not stored yet.
    DOWNLOAD_CAPE = "download_cape"  # Downloading a cape that is not stored yet.
    SAVE = "save"  # Writing the player, skin, and cape rows.
    DONE = "done"


class SkinManagerError(Exception):
    """Base class for Skin Manager failures an operator should report to the user."""


class DefaultSkinError(SkinManagerError):
    """Raised when a player uses a default skin, so there is no texture to download."""


class SkinNotStoredError(SkinManagerError):
    """Raised when the requested player or skin index is not stored."""


class SyncCancelledError(SkinManagerError):
    """Raised when a sync stops because its cancel check returned true."""


class MissingTextureError(SkinManagerError):
    """Raised when a stored skin's file is gone from disk. A re-sync downloads it again."""


@dataclass(frozen=True, slots=True)
class SyncResult:
    """The outcome of `SkinManager.sync`. `downloaded` is true if any file was fetched."""

    player: Player
    skin: Skin
    cape: Cape | None
    downloaded: bool


@dataclass(frozen=True, slots=True)
class Selection:
    """A stored skin ready to apply: its absolute file path and arm model."""

    path: Path
    model: SkinModel


@dataclass(frozen=True, slots=True)
class ImportReport:
    """The outcome of `SkinManager.import_legacy_dir`."""

    imported: tuple[Player, ...]
    failed: tuple[tuple[Path, str], ...]  # (file, reason) for each file that was skipped.


def route(has_local: bool, online: bool, prompt: bool) -> Route:
    """Decide what the router does with a username.

    `has_local` is whether the player has a stored skin, `online` is Blender's
    Online Access setting, and `prompt` is the add-on preference that asks
    before refreshing stored players.
    """
    if has_local:
        return Route.PROMPT if online and prompt else Route.LOAD
    return Route.DOWNLOAD if online else Route.OFFLINE_ERROR


def texture_filename(kind: str, texture_hash: str) -> str:
    """Return the file name of a texture, such as ``skin_<hash>.png``."""
    return f"{kind}_{texture_hash}.png"


def stage_progress(stage: SyncStage) -> float:
    """Return how far a sync is at `stage`, from above 0 to 1 at `SyncStage.DONE`."""
    stages = list(SyncStage)
    return (stages.index(stage) + 1) / len(stages)


def stage_text(stage: SyncStage, name: str) -> str:
    """Return a short status message for `stage`, naming the player."""
    match stage:
        case SyncStage.LOOKUP:
            return f"Looking up {name}"
        case SyncStage.PROFILE:
            return f"Fetching {name}'s profile"
        case SyncStage.DOWNLOAD_SKIN:
            return f"Downloading {name}'s skin"
        case SyncStage.DOWNLOAD_CAPE:
            return f"Downloading {name}'s cape"
        case SyncStage.SAVE:
            return f"Saving {name}'s skin"
        case SyncStage.DONE:
            return f"Got {name}'s skin"


class SkinManager:
    """Facade over the skin tables, Mojang, and the player data folder.

    The caller passes in everything that depends on Blender::

        manager = SkinManager(
            db_session,
            MojangClient(HTTPClient()),
            Path(storage_dir(StorageDir.PLAYER_DATA)),
            Path(storage_dir(StorageDir.PLAYER_DATA_PURGED)),
        )
        result = asyncio.run(manager.sync(username))

    Each method opens its own short database sessions. No session is ever held
    open across network I/O.
    """

    def __init__(self, session: SessionFactory, mojang: MojangClient,
                 player_data_dir: Path, purged_dir: Path):
        self.session = session
        self.mojang = mojang
        self.player_data_dir = Path(player_data_dir)
        self.purged_dir = Path(purged_dir)
        self._listeners: list[SyncListener] = []

    # region Observer

    def subscribe(self, listener: SyncListener) -> Callable[[], None]:
        """Call `listener` at each `SyncStage`. Returns a function that unsubscribes it."""
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    def _notify(self, stage: SyncStage, name: str) -> None:
        for listener in tuple(self._listeners):
            listener(stage, name)

    # endregion

    @contextmanager
    def _db(self) -> Generator[SkinDatabase]:
        """Open a session, make sure the schema exists, and yield the tables."""
        with self.session() as conn:
            db = SkinDatabase(conn)
            db.create_schema()
            yield db

    def player_dir(self, uuid: str) -> Path:
        """Return the folder that holds a player's hash-named textures."""
        return self.player_data_dir / normalize_uuid(uuid)

    def find_local(self, name: str) -> Player | None:
        """Return the stored player named `name` if they have at least one skin, else `None`.

        The router uses this for `route`'s `has_local`. The name is matched as
        last synced, so a player renamed since then is found again after the
        next sync.
        """
        with self._db() as db:
            player = db.find_player(name.strip())
            if player is None or db.latest_skin(player.uuid) is None:
                return None
            return player

    def saved_skins(self, name: str) -> list[Skin]:
        """Return the stored skins of the player named `name`, newest first. Empty if none.

        The name is matched as last synced, like `find_local`.
        """
        with self._db() as db:
            player = db.find_player(name.strip())
            return list(reversed(db.skins(player.uuid))) if player is not None else []

    def skin_path(self, skin: Skin) -> Path:
        """Return the absolute path of a stored skin's file."""
        return self.player_data_dir / skin.path

    async def sync(self, name: str, should_cancel: CancelCheck | None = None) -> SyncResult:
        """Fetch a player's current skin and cape, downloading only textures not stored yet.

        Replaces the legacy "get" and "add" operators. A skin already stored
        with the same hash and model is reused. If a download fails, no rows
        are written and files downloaded by this call are removed.

        `should_cancel` is checked before each stage and before the database
        write. Once it returns true, the sync stops with `SyncCancelledError`,
        with the same cleanup as a failed download.

        Raises `PlayerNotFoundError` for an unknown name, `DefaultSkinError`
        if the player has no custom skin, `SyncCancelledError` when cancelled,
        and `NetworkError`, `MojangFormatError`, `SchemaVersionError`, or
        `OSError` otherwise.
        """

        def checkpoint() -> None:
            if should_cancel is not None and should_cancel():
                raise SyncCancelledError("Skin download cancelled")

        checkpoint()
        self._notify(SyncStage.LOOKUP, name)
        uuid, canonical = await self.mojang.lookup(name)
        checkpoint()
        self._notify(SyncStage.PROFILE, canonical)
        profile = await self.mojang.profile(uuid)
        if profile.skin is None:
            raise DefaultSkinError(f"{profile.name} uses a default skin, so there is nothing to download")

        # Read what is stored in a short session that closes before any download.
        with self._db() as db:
            stored_skin = db.find_skin(uuid, profile.skin.hash)
            if stored_skin is not None and stored_skin.model != profile.skin.model:
                stored_skin = None  # Same texture, new arm model: store a new row for the same file.
            stored_cape = db.find_cape(uuid, profile.cape.hash) if profile.cape else None

        skin_path = self._relative(uuid, "skin", profile.skin)
        cape_path = self._relative(uuid, "cape", profile.cape) if profile.cape else None

        new_files: list[Path] = []
        try:
            checkpoint()
            await self._fetch(profile.skin, skin_path, SyncStage.DOWNLOAD_SKIN, canonical, new_files)
            if profile.cape is not None and cape_path is not None:
                checkpoint()
                await self._fetch(profile.cape, cape_path, SyncStage.DOWNLOAD_CAPE, canonical, new_files)

            checkpoint()
            self._notify(SyncStage.SAVE, canonical)
            with self._db() as db:
                player = db.upsert_player(uuid, profile.name)
                skin = stored_skin or db.add_skin(uuid, profile.skin.hash, skin_path, profile.skin.model)
                cape = None
                if profile.cape is not None and cape_path is not None:
                    cape = stored_cape or db.add_cape(uuid, profile.cape.hash, cape_path)
        except BaseException:
            for path in new_files:
                path.unlink(missing_ok=True)
            raise

        self._notify(SyncStage.DONE, canonical)
        return SyncResult(player, skin, cape, downloaded=bool(new_files))

    def _relative(self, uuid: str, kind: str, texture: TextureRef) -> str:
        """Return the texture's path relative to the player data folder, with ``/`` separators."""
        return f"{normalize_uuid(uuid)}/{texture_filename(kind, texture.hash)}"

    async def _fetch(self, texture: TextureRef, relative: str, stage: SyncStage,
                     name: str, new_files: list[Path]) -> None:
        """Download `texture` unless its file already exists, recording a new file in `new_files`.

        A row whose file was deleted is repaired here, because the file is
        downloaded again to the same path.
        """
        dest = self.player_data_dir / relative
        if dest.is_file():
            return
        self._notify(stage, name)
        await self.mojang.http.download(texture.url, dest)
        new_files.append(dest)

    def selection(self, uuid: str, index: int = -1) -> Selection:
        """Return the stored skin at `index` (-1 for the newest) ready to apply.

        Raises `SkinNotStoredError` if there is no such skin, and
        `MissingTextureError` if its file is gone, so the operator can offer a
        re-sync.
        """
        with self._db() as db:
            skin = db.skin(uuid, index)
        if skin is None:
            raise SkinNotStoredError(f"No stored skin at index {index}")
        path = self.skin_path(skin)
        if not path.is_file():
            raise MissingTextureError(f"The skin file {path.name} is missing; sync the player again")
        return Selection(path, skin.model)

    def purge(self, uuid: str, backup: bool) -> bool:
        """Delete a player's rows, then back up or delete their texture folders.

        Rows go first, so a failed file step never leaves rows that point at
        nothing. The folders are the player's UUID folder plus any legacy
        username folder their stored paths point into. With `backup`, each is
        moved to the purged folder as ``<folder>_<n>``. Returns whether the
        player was stored.
        """
        uuid = normalize_uuid(uuid)
        with self._db() as db:
            paths = [t.path for t in (*db.skins(uuid), *db.capes(uuid))]
            existed = db.delete_player(uuid)

        for folder in self._player_folders(uuid, paths):
            if backup:
                self.purged_dir.mkdir(parents=True, exist_ok=True)
                folder.rename(self._backup_path(folder.name))
            else:
                shutil.rmtree(folder)
        return existed

    def _player_folders(self, uuid: str, paths: list[str]) -> list[Path]:
        """Return the existing folders holding a player's files, each directly inside the player data folder.

        Anything outside the player data folder, or the folder itself, is never
        returned, so a bad stored path cannot purge unrelated files.
        """
        root = self.player_data_dir.resolve()
        candidates = [self.player_dir(uuid), *((self.player_data_dir / p).parent for p in paths)]
        folders: list[Path] = []
        for candidate in candidates:
            folder = candidate.resolve()
            if folder.parent == root and folder.is_dir() and folder not in folders:
                folders.append(folder)
        return folders

    def _backup_path(self, name: str) -> Path:
        """Return the first free ``<purged>/<name>_<n>`` path, counting from 1."""
        n = 1
        while (path := self.purged_dir / f"{name}_{n}").exists():
            n += 1
        return path

    def import_legacy_dir(self, folder: Path) -> ImportReport:
        """Import every legacy ``<name>/<name>_Data.json`` file under `folder`.

        Each file is imported in its own transaction, so one bad file never
        blocks the others. Files that cannot be read or do not have the legacy
        layout are listed in `ImportReport.failed` with the reason.
        """
        imported: list[Player] = []
        failed: list[tuple[Path, str]] = []
        for file in sorted(Path(folder).glob(LEGACY_GLOB)):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                with self._db() as db:
                    imported.append(db.import_legacy(data))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
                failed.append((file, f"could not be read: {error}"))
            except (LegacyFormatError, sqlite3.IntegrityError) as error:
                failed.append((file, str(error)))
        return ImportReport(tuple(imported), tuple(failed))


class SyncProgress:
    """The one background sync that may run at a time, and how far it has got.

    Pattern: Singleton. Operators, the panel, and the file-load handler all
    read the module-level `sync_progress`, so there is exactly one place that
    knows whether a sync is running. Tests build their own instance, and
    `reset()` clears it on unregister.
    """

    def __init__(self):
        self.task: BackgroundTask[SyncResult] | None = None
        self.name = ""
        self.stage: SyncStage | None = None
        self.cancelling = False

    @property
    def running(self) -> bool:
        """Whether a sync has started and not been finished or reset."""
        return self.task is not None

    def start(self, name: str, task: BackgroundTask[SyncResult]) -> None:
        """Record that `task` is syncing `name`. Raises `RuntimeError` if one is already running."""
        if self.running:
            raise RuntimeError("A skin sync is already running")
        self.reset()
        self.task, self.name = task, name

    def update(self, events: Iterable[tuple[SyncStage, str]]) -> None:
        """Apply `(stage, name)` events drained from the task, oldest first."""
        for stage, name in events:
            self.stage, self.name = stage, name

    def cancel(self) -> None:
        """Ask the running sync, if any, to stop at its next checkpoint."""
        if self.task is not None:
            self.task.cancel()
            self.cancelling = True

    def reset(self) -> None:
        """Forget the current sync. Does not cancel it; call `cancel()` first for that."""
        self.task = None
        self.name = ""
        self.stage = None
        self.cancelling = False

    @property
    def fraction(self) -> float:
        """Progress from 0 to 1, for a progress bar."""
        return stage_progress(self.stage) if self.stage is not None else 0.0

    @property
    def text(self) -> str:
        """A short status message for the current stage."""
        if self.cancelling:
            return f"Cancelling {self.name}'s download"
        if self.stage is None:
            return f"Starting {self.name}'s download"
        return stage_text(self.stage, self.name)


# The process-wide sync state. See `SyncProgress`.
sync_progress = SyncProgress()
