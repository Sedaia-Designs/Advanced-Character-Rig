# Skin Manager implementation plan

Internal planning document for finishing the Skin Manager rewrite (extension
4.0.0). It replaces the legacy skin utility in `.legacy/`. Keep the status table
current as phases land, and delete this file once the Skin Manager ships.

Written 2026-11-07.

## Status

| Layer | Code | State |
|---|---|---|
| SQLite factory and schema versions | `core/sql.py`, `core/databases/schema.py` | Done, tested |
| Skin tables and legacy JSON import | `core/databases/skins.py` | Done, tested |
| HTTPS client | `core/network.py` | Done, tested |
| Constants (IDs, rig names, enums) | see [Constants](#constants) | Done |
| Rig targets (rig-agnostic Skin Manager) | `core/skin_targets.py`, `features/SACR_R7_UI3/constants.py` | Done, tested |
| Mojang adapter | `core/mojang.py` | Done, tested (`tests/test_mojang.py`) |
| Skin Manager service | `core/skin_manager.py` | Phase 2. Only `Route` exists |
| Operators | `features/skin_manager/operators/` | Phase 3. `SkinRouter` has a target-based `poll` and reads the username, then stops; `SkinAdd` is a stub |
| Menus and panel | `features/skin_manager/menus/`, `panels/` | Phase 4. Empty |
| Changelog and public docs | `CHANGELOG.md`, docs site | Phase 5 |

## R7.5 rig data contract

Checked read-only against `lib/SACR.R7.5.0.blend` in Blender 5.2.

- Armature data `rigID` is `"SACR.Rev_7.UI_3"`.
- The `PythonConfig.Skin` bone holds `Username` (str), `SyncArms` (bool), and
  `SyncName` (bool). The settings live on this bone, not the scene; the
  changelog line saying they moved to the scene is wrong and needs fixing.
- `PythonConfig.Materials["skin"]` is the `Skin` material. Its Image Texture
  node `Skin_Texture` uses the image `Skin`, which is packed.
- `Rig_Properties["Arm Type"]` is an int enum: `0` Default, `1` Slim, `2` Super-Slim.
- There is no `"Rig Name"` data property any more (the legacy `SyncName`
  wrote one). The rig's collection is `Default - SACR R7.5.0`.

## Rig targets

The Skin Manager names no rig. Each rig feature describes where its rig keeps
skin data with a `core.skin_targets.SkinTarget` and adds it to
`core.skin_targets.registry` in its `register()`. Skin Manager operators call
`registry.for_rig(context.active_object)` and use only the names the target
gives them.

| `SkinTarget` field | Meaning | R7.5.0 value |
|---|---|---|
| `label` | Rig name for reports | `"SACR R7.5.0"` |
| `rig_id_property`, `rig_ids` | Which armatures match | `rigID` in `{"SACR.Rev_7.UI_3"}` |
| `username` | `BoneProp` holding the username | `PythonConfig.Skin["Username"]` |
| `skin` | `TextureSlot`: material pointer and image node | `PythonConfig.Materials["skin"]`, node `Skin_Texture` |
| `arm_type` | Optional `ArmTypeSync`: toggle, target, and `SkinModel` → value map | toggle `PythonConfig.Skin["SyncArms"]`, target `Rig_Properties["Arm Type"]`, classic → 0, slim → 1 |
| `sync_name` | Optional toggle for renaming the rig after the player | `PythonConfig.Skin["SyncName"]` |

An optional field left as `None` is a feature the rig does not have, and the
Skin Manager skips that step. Supporting another rig means writing one
`SkinTarget` in that rig's feature; the Skin Manager does not change.

## Constants

All of these are in place. Every value is explicit, so renaming a member never
changes a public idname or a stored value.

| Module | Members |
|---|---|
| `core/mojang.py` | `TEXTURE_HOST`, `MojangURL` (`PROFILES`, `SESSION`, `TEXTURES`). Moved here from the feature so the core adapter can use it. Phase 1 added `TextureRef`, `Profile`, `MojangClient`, `MojangFormatError`, and `PlayerNotFoundError` |
| `core/skin_manager.py` | `Route` (`LOAD`, `PROMPT`, `DOWNLOAD`, `OFFLINE_ERROR`) |
| `core/skin_targets.py` | `BoneProp`, `TextureSlot`, `ArmTypeSync`, `SkinTarget`, `SkinTargetRegistry`, `registry` |
| `features/SACR_R7_UI3/constants.py` | `RigID`, `RigBone`, `SkinProp`, `MaterialKey`, `SkinNode`, `RigProp`, `ArmType` (`DEFAULT=0`, `SLIM=1`, `SUPER_SLIM=2`), `SKIN_TARGET` |
| `features/skin_manager/constants.py` | `NAMESPACE` only |
| `features/skin_manager/operators/constants.py` | `OperatorID`: `ROUTER`, `ADD`, `LOAD`, `PURGE`, `IMPORT_LEGACY` |
| `features/skin_manager/menus/constants.py` | `MenuID.EXISTING` |
| `features/skin_manager/panels/constants.py` | `PanelID.MAIN` |
| `preferences/constants.py` | `StorageDir.PLAYER_DATA_PURGED` |

## Legacy behaviour to carry over

The legacy flow is router → get / add / load / purge. Keep the behaviour, and
fix these legacy bugs instead of porting them:

- `.strip(url)` strips characters rather than a prefix, so it corrupts hashes.
  Take the last URL path segment instead.
- `PlayerModel` is unbound when the model is not slim.
- `skin_add` computes the cape index from the skins list.
- Player folders are keyed by username, so a renamed player loses their history.
- Purge with backup runs `skin_get` twice.
- No request timeouts, and bare `except` blocks.

## Phase 1: Mojang adapter (`core/mojang.py`)

**Done 2026-11-08.** Built as specified, with these additions that Phase 2
relies on:

- Mojang sends texture URLs as plain `http://`, which `HTTPClient` refuses. An
  accepted URL is rebuilt from its hash as `MojangURL.TEXTURES + hash`, so
  `TextureRef.url` is always HTTPS.
- `TextureRef.hash` is checked to be lowercase hex, so Phase 2 can put it in
  file names (`skin_<hash>.png`) without further checks.
- The `textures` property is found by name, not taken from `properties[0]`.
- `lookup` URL-encodes the name as one path segment and raises
  `PlayerNotFoundError` for an empty name without sending a request.
- `profile` also raises `PlayerNotFoundError` for an unknown UUID (HTTP 404 or
  204), and `ValueError` for a malformed UUID argument.
- `MojangFormatError` subclasses `ValueError`. The parsers `parse_lookup`,
  `parse_profile`, and `parse_texture` are public, so they can be tested
  without a client.

Original spec:

Pattern: Adapter + Facade, with `HTTPClient` injected as the Strategy.

- Records: `TextureRef(url, hash, model: SkinModel | None)` and
  `Profile(uuid, name, skin: TextureRef | None, cape: TextureRef | None)`.
- `MojangClient(http)`:
  - `async lookup(name) -> (uuid, name)`. Raises `PlayerNotFoundError`, a
    subclass of `NotFoundError`.
  - `async profile(uuid) -> Profile`. Base64-decodes `properties[0].value` and
    reads `textures.SKIN.metadata.model`.
- Only accept texture URLs whose host is `TEXTURE_HOST`. `HTTPClient` enforces
  HTTPS but not the host, and these URLs come from a server response.
- Every malformed response raises one `MojangFormatError`. Code past the adapter
  never sees raw JSON.
- Tests (`tests/test_mojang.py`), with a fake opener: slim, classic, cape, and
  no-cape profiles; a 404 username; malformed base64; a foreign texture host.

## Phase 2: Skin Manager service (`core/skin_manager.py`)

Pattern: Facade over `SkinDatabase`, `MojangClient`, and the player data folder.
Progress is published through Observer callbacks.

- `route(name, has_local, online, prompt) -> Route`, a pure function, so the
  router's decision is testable without `bpy`.
- `async sync(name) -> SyncResult(player, skin, cape, downloaded: bool)`:
  1. Fetch the profile before opening a database transaction. Never hold an
     SQLite transaction across network I/O.
  2. If `find_skin(uuid, hash)` hits, reuse that row and skip the download. One
     operation replaces the legacy "get" and "add".
  3. Otherwise download to `playerdata/<uuid>/skin_<hash>.png` (and
     `cape_<hash>.png`), then `upsert_player` and `add_skin` / `add_cape` in one
     session. Store paths relative to the player data folder.
  4. Naming files by hash means no index collisions, no overwrites, and no
     usernames in paths.
- `selection(uuid, index=-1) -> Selection(abs_path, model)`. Raises if the
  file is missing, so the operator can offer a re-sync.
- `purge(uuid, backup: bool)`: delete the rows first, then move the folder to
  `playerdata_purged/<uuid>_<n>` or delete it. A failed file step then never
  leaves rows that point nowhere.
- `import_legacy_dir(dir) -> ImportReport(imported, failed: list[(file, reason)])`.
  Wraps `parse_legacy` / `import_legacy`, with one transaction per file.
- Tests (`tests/test_skin_manager.py`), with in-memory SQLite, a temporary
  folder, and a fake `MojangClient`: dedupe by hash, a renamed player keeping
  their history, no partial rows after a failed download, purge with and without
  backup, and a folder with both good and bad legacy files.

## Phase 3: Operators (`features/skin_manager/operators/`)

| `OperatorID` | idname | Role |
|---|---|---|
| `ROUTER` | `skin_router` | Read `Username`, call `route()`, then dispatch or open `MenuID.EXISTING` |
| `ADD` | `skin_add` | Sync from Mojang (download only when the hash is new), then apply |
| `LOAD` | `skin_load` | `index: IntProperty(default=-1, min=-1)`; apply a stored skin offline |
| `PURGE` | `skin_purge` | `backup: BoolProperty`; `invoke_confirm`, then re-sync |
| `IMPORT_LEGACY` | `skin_import_legacy` | Import `playerdata/*/*_Data.json` and report the counts |

Rules shared by every operator:

- `poll` returns `registry.for_rig(context.active_object) is not None`.
  `execute` looks the target up again and reports an error if a bone it names
  is missing.
- Check `bpy.app.online_access` before any network call.
- Catch only `NetworkError`, `MojangFormatError`, `SchemaVersionError`, and
  `OSError`. Report with `self.report({"ERROR"}, ...)` and return `{"CANCELLED"}`.

Applying a skin (`LOAD`; `ADD` calls it):

1. Unpack the `Skin` image if it is packed, set `filepath` to the absolute path,
   then `reload()` and `pack()`. Packing keeps shared `.blend` files portable.
   The image node comes from `target.skin`.
2. If `target.arm_type` is set and its toggle is on, write
   `target.arm_type.value_for(model)` to `target.arm_type.target`.
3. If `target.sync_name` is set and on, call the shared `OperatorID.RIG_RENAME`.

Async: for 4.0.0, run `asyncio.run(manager.sync(name))` inside `execute`. Every
request has a 10 s timeout, and two small PNGs usually take about a second. A
modal or timer version with progress reporting can come later; the Phase 2
Observer callbacks already support it.

## Phase 4: Menus and panel

- `MenuID.EXISTING`, replacing the legacy "regen" menu: *Load saved skin*,
  *Check for new skin*, *Purge...*. The purge confirmation is `invoke_confirm`
  on `PURGE` rather than a separate menu.
- `PanelID.MAIN`, the *Skin Manager* panel, with the same `poll` as the
  operators. It contains:
  - the `Username` field
  - a *Change Skin* button for `ROUTER`
  - an *Open player data* button for `FILE_OPEN` on `StorageDir.PLAYER_DATA`
  - the `SyncArms` and `SyncName` toggles
  - optionally, a read-only history list from `SkinDatabase.skins()` that calls
    `LOAD(index)`
- Preferences: an *Import legacy player data* button next to the existing
  `prompt_to_refresh_player_data`.

## Phase 5: Wrap-up

- `CHANGELOG.md`: list the full operator set in the 4.0.0 entry, and fix the
  "skin settings moved to the scene" line.
- Docs site: remove the "no panel yet" note from `skin-system/index.md`, add
  `skin-system/mojang.md`, and update the Skin Manager section of
  `development/blender-ids.md`.
- Docs site: document `SkinTarget` for anyone adding a rig.
- Run compileall, Pyright, and the new tests.
- Manual checks in Blender 5.2:
  - registration and unregistration
  - offline refusal
  - a new player, the same skin again (no download), and a changed skin
  - a slim skin sets `Arm Type` to 1
  - rename sync
  - purge with and without backup
  - legacy import
  - save, reopen, and confirm the skin is still packed

## Open decisions

1. **Panel location:** a sub-panel of the **SACR Config** sidebar (recommended,
   since the rig check is already there), or its own sidebar tab like the legacy
   "Download Skins"? `PanelID.MAIN` works either way.
2. **What `SyncName` renames:** R7.5 has no `"Rig Name"` property. Should it
   rename the object, the armature data, and the collection to
   `"<Username> - SACR R7.5"`?
3. **Legacy import:** a manual button (recommended) or automatic on first run?
4. **Purge backup:** keep it (a folder move is cheap) or drop it, since
   hash-named history makes purging rare? `StorageDir.PLAYER_DATA_PURGED` is
   in place in case it stays.
5. **Blocking `asyncio.run` for 4.0.0:** acceptable, or should the modal
   version be in scope now?
