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
| Skin Manager service | `core/skin_manager.py` | Done, tested (`tests/test_skin_manager.py`) |
| Operators | `features/skin_manager/operators/` | Done, validated in Blender 5.2.2 |
| Background sync with progress | `core/background.py`, `core/skin_manager.py`, `features/skin_manager/operators/` | Done, tested, validated in the Blender 5.2.2 UI |
| Menus and panel | `features/skin_manager/menus/`, `panels/`, `preferences/` | Done, validated in the Blender 5.2.2 UI |
| Changelog and public docs | `CHANGELOG.md`, docs site | Done |

## Finishing a phase

A phase is not done until all of these steps are complete. Do them in this
order, after the phase's checks (compileall, Pyright, and its tests) pass:

1. **Record completion here.** Mark the phase done in the
   [Status](#status) table, update the [Constants](#constants) table if the
   phase added public names, and add a dated "Done" note under the phase
   listing anything that differs from its spec.
2. **Update the documentation site.** Add or update the pages on
   `docs.sakura-sedaia.com` (SACR 7.5.0 section) that cover the code the phase
   added or changed: user pages under `extension/` for what users see, and
   `development/` pages, such as `development/skin-manager/` for the
   service, or `development/blender-ids.md` for new operators.
3. **Commit.** Commit the phase's code, tests, and this plan's updates
   together, with a message naming the phase. Commit the docs site changes in
   the docs site repository.

Phase 5 still does the final changelog and docs pass for the whole feature.

## R7.5 rig data contract

Checked read-only against `../lib/SACR.B7.5.0_RC4.blend` in Blender 5.2.

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
| `core/skin_manager.py` | `Route` (`LOAD`, `PROMPT`, `DOWNLOAD`, `OFFLINE_ERROR`). Phase 2 added `SyncStage`, `SkinManager`, `SyncResult`, `Selection`, `ImportReport`, `SkinManagerError` (`DefaultSkinError`, `SkinNotStoredError`, `MissingTextureError`), `route`, `texture_filename`, and `LEGACY_GLOB` |
| `core/skin_targets.py` | `BoneProp`, `TextureSlot`, `ArmTypeSync`, `SkinTarget`, `SkinTargetRegistry`, `registry` |
| `features/SACR_R7_UI3/constants.py` | `RigID`, `RigBone`, `SkinProp`, `MaterialKey`, `SkinNode`, `RigProp`, `ArmType` (`DEFAULT=0`, `SLIM=1`, `SUPER_SLIM=2`), `SKIN_TARGET` |
| `features/skin_manager/constants.py` | `NAMESPACE` only |
| `features/skin_manager/operators/constants.py` | `OperatorID`: `ROUTER`, `ADD`, `LOAD`, `PURGE`, `IMPORT_LEGACY` |
| `features/skin_manager/menus/constants.py` | `MenuID.EXISTING` |
| `features/skin_manager/panels/constants.py` | `PanelID.MAIN`, `PanelID.HISTORY` (Phase 4), `CATEGORY = "Skins"` |
| `constants.py` | `StorageDir.PLAYER_DATA_PURGED` |

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

**Done 2026-11-08.** Built as specified, with these differences that Phase 3
relies on:

- `route(has_local, online, prompt)` takes no name; the decision does not use
  it. `SkinManager.find_local(name)` supplies `has_local`: the stored player
  with that name, if they have at least one skin.
- `SkinManager(session, mojang, player_data_dir, purged_dir)` takes the
  session factory (`preferences.access.db_session`) and both folders as
  arguments. Each method opens its own short sessions and creates the schema
  if needed.
- Dedupe is by hash and model: the same texture with a new arm model gets a
  new row pointing at the same file. A row whose file was deleted is repaired
  by the next `sync`, which downloads to the same path.
- Downloads run one after another, not with `asyncio.gather`, so files from a
  failed sync can be removed safely. If any download fails, no rows are written
  and files downloaded by that call are deleted.
- New errors for operators to report: `DefaultSkinError` (player has a default
  skin), `SkinNotStoredError`, and `MissingTextureError`, all subclasses of
  `SkinManagerError`. **Phase 3 must add `SkinManagerError` to its catch list.**
- `purge` also moves or deletes legacy username folders that the player's
  stored paths point into, but never a folder outside the player data folder.
  Backups are `<folder>_<n>` from 1. It returns whether the player was stored.
- `import_legacy_dir` returns `ImportReport(imported: tuple[Player, ...],
  failed: tuple[(Path, reason), ...])`.
- Known gap: `SkinDatabase.import_legacy` replaces a player's existing rows, so
  importing a legacy file after syncing that player drops the synced rows (the
  files stay). Phase 4 should warn about this next to the import button, or the
  import should skip players who are already stored.
- Observer stages are `SyncStage`: `LOOKUP`, `PROFILE`, `DOWNLOAD_SKIN`,
  `DOWNLOAD_CAPE`, `SAVE`, `DONE`.

Original spec:

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

**Done 2026-11-08.** All five operators are registered. Differences from the
spec, and decisions Phase 4 relies on:

- `operators/base.py` holds the shared Blender glue: the `SkinOperator` mixin
  (`poll`, target, bone, and username lookups with their error reports),
  `build_manager()`, `REPORTED_ERRORS`, and `call_operator()`. Its docstring
  says why it is shared. Skin application lives only in `load.py`.
- `call_operator(caller, idname, **props) -> bool` catches the `RuntimeError`
  that `bpy.ops` raises when a nested operator reports an error, and reports
  the message again through the caller, so users see the message instead of a
  traceback.
- `IMPORT_LEGACY` has no rig `poll`, because Phase 4 runs it from the
  preferences. It takes a `directory` (file browser on invoke), defaulting to
  `StorageDir.PLAYER_DATA`.
- `ROUTER` on `Route.PROMPT` opens `MenuID.EXISTING` if it is registered, and
  otherwise runs `ADD`. Phase 4 only has to register the menu.
- `LOAD` checks every bone, the material, and the image before changing
  anything, and refuses an image linked from a library. It drops the packed
  copy with `unpack(method="REMOVE")`, which writes nothing to disk, then sets
  `filepath`, reloads, and packs.
- Open decision 2, decided 2026-11-08: `SyncName` calls `RIG_RENAME` with
  `"<player> - <target.label>"` (`Notch - SACR R7.5.0`). The collection is
  renamed only if it already ends in `" - <target.label>"`, like the default
  `Default - SACR R7.5.0`.
- Open decision 5: `ADD` blocks with `asyncio.run`. Replaced by Phase 3b.
- Labels: *Change Skin* (`ROUTER`), *Check for New Skin* (`ADD`), *Load Saved
  Skin* (`LOAD`), *Purge Player Data* (`PURGE`), *Import Legacy Player Data*
  (`IMPORT_LEGACY`).

Validated in Blender 5.2.2 in the background against `../lib/SACR.B7.5.0_RC4.blend`,
with isolated user resources: registration and unregistration, `poll`, an
empty username, offline refusals, a new player, the same skin again, a stored
player through the router, loading by index and a bad index, Arm Type set to 0
for a classic skin, rig and collection rename, purge with and without backup,
an unknown player, legacy import with one bad file, and the skin still packed
after save and reopen. Not validated: a slim skin setting Arm Type to 1, the
purge confirmation dialog and the import file browser (both need the UI), and a
rig linked from a library.

Original spec:

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
- Catch only `NetworkError`, `MojangFormatError`, `SkinManagerError`,
  `SchemaVersionError`, and `OSError`. Report with `self.report({"ERROR"}, ...)` and return `{"CANCELLED"}`.

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

## Phase 3b: Background sync with progress

**Done 2026-11-08.** Built as planned, with Esc cancelling (Open Decision 6,
taken at its default). Differences and details Phase 4 relies on:

- `SyncProgress` and its `sync_progress` instance live in
  `core/skin_manager.py`, not the Blender layer, because they need no `bpy`
  and can be tested. The panel reads `sync_progress.running`, `.fraction`,
  and `.text`. `stage_text(stage, name)` gives the per-stage messages.
- `BackgroundTask()` is created first, so the manager's events can be
  subscribed to `task.publish` before `task.start(make_coro)` runs the work.
- `SkinOperator.blocked_while_syncing` marks `ADD`, `PURGE`, and `ROUTER`.
  `LOAD` stays available during a sync.
- `ROUTER` and `PURGE` get a hidden, unsaved `use_modal` property, set in
  `invoke`, that chooses `INVOKE_DEFAULT` or `EXEC_DEFAULT` for `ADD`.
  `PURGE`'s confirmation keeps the property.
- `ADD` applies the result to the rig the sync started on, using
  `temp_override(active_object=rig)`, so a change of selection during the wait
  does not matter. If the rig's username changed during the wait, it saves the
  skin but does not apply it.
- `ADD.cancel()` (Blender ending the modal operator) and the `load_pre`
  handler both cancel the task and clear `sync_progress`.

Validated:

- Unit tests: 137 pass (`tests/test_background.py`, plus cancellation and
  progress tests in `tests/test_skin_manager.py`).
- Background Blender: the Phase 3 script through `execute`, 16/16 offline and
  26/26 online, including `poll` refusing a second sync while one runs.
- Blender UI with event simulation:
  - `INVOKE_DEFAULT` returns `RUNNING_MODAL`
  - Esc cancels, leaving no files and an unchanged image
  - the router starts the modal sync, and the progress stages advance
  - the skin is applied and Arm Type synced
  - deleting the rig mid-sync leaves no stuck state
  - loading another file mid-sync cancels the worker
    (`SyncCancelledError`) and clears the state

Not validated: how the status bar text looks (Blender has no API to read it
back), and the panel progress bar, which arrives in Phase 4.

Original plan:

Decided 2026-11-08: `ADD` must not freeze Blender while it downloads, and it
should show progress. Do this before Phase 4, because the panel draws the
progress state this phase adds.

### Approach: a modal operator on Blender's event loop

The download runs on a worker thread. A modal operator keeps Blender's own
event loop in charge, so the UI stays responsive. The operator wakes on a
window manager timer (`event_timer_add`, every 0.1 s), reads progress, updates
the UI, and applies the skin on the main thread when the work is finished.

`bpy` is not thread-safe, so the worker thread never touches it. It only runs
`SkinManager.sync`, which is already free of `bpy`.

Rejected alternative: `bpy.app.timers`. A timer callback has no operator, so it
cannot use `self.report`, catch Esc, or push an undo step, and it outlives a
file load.

### Core (`core/`, tested without Blender)

1. **`core/background.py`: `BackgroundTask`.** Pattern: Facade over
   `threading`, `asyncio`, and `queue`, with Observer events.
   - `BackgroundTask.start(make_coro)` starts a daemon thread that runs
     `asyncio.run(make_coro(task))`, so the coroutine gets its own event loop.
   - `publish(event)` may be called from the worker. It puts the event on a
     `queue.SimpleQueue`, and `drain()` returns the queued events on the main
     thread.
   - `done()`, plus `result()`, which returns the value or re-raises the
     worker's exception on the main thread.
   - `cancel()` sets a `threading.Event`, and `cancelled()` reads it.
   - The thread cannot be killed while it waits on a socket, so cancelling
     only stops the work at the next checkpoint. The `HTTPClient` timeout
     limits how long that takes.
2. **Cancellation in `SkinManager.sync(name, should_cancel=None)`.**
   `should_cancel` is a `Callable[[], bool]` Strategy, checked before each
   stage and before the database write. It raises `SyncCancelledError`, a
   subclass of `SkinManagerError`. The existing cleanup already removes files
   downloaded by that call and writes no rows.
3. **`stage_progress(stage) -> float`**, a pure function that maps each
   `SyncStage` to a value from 0 to 1 for progress bars. `DONE` is 1.
4. **No `bpy` calls from the worker.** `build_manager()` currently passes
   `preferences.access.db_session`, which calls `extension_path_user` and so
   would run `bpy` on the worker thread. Instead, resolve the database path on
   the main thread and pass `SQLite(path).session`. Each session opens and
   closes its own connection on the worker thread, which `sqlite3` allows.

### Blender layer (`features/skin_manager/operators/`)

1. **`ADD` gets `invoke` and `modal`, and keeps `execute`.**
   - `invoke` checks Online Access, the rig, and the username. It stores the
     rig's name, not the object, because an undo or rename during the wait
     makes an object reference invalid. It then builds the manager on the
     main thread, starts the `BackgroundTask` with
     `manager.sync(name, should_cancel=task.cancelled)`, and subscribes
     `task.publish` to the manager's `SyncStage` events. Finally it adds the
     timer and the modal handler, and returns `{"RUNNING_MODAL"}`.
   - `modal` on `TIMER` drains the events and updates the progress state. Once
     the task is done, it removes the timer, clears the status text, and calls
     `result()`. It reports errors from `REPORTED_ERRORS`, or looks the rig up
     again by name and runs `LOAD` with the synced index. If the rig no longer
     exists, it reports that the skin was saved and can be applied with *Load
     Saved Skin*.
   - `modal` on `ESC` calls `task.cancel()` and keeps running until the task
     ends, then reports "Cancelled". It returns `{"PASS_THROUGH"}` for every
     other event, so the user can keep working.
   - `execute` stays blocking. Scripts call operators with `EXEC_DEFAULT`, and
     background mode (`blender -b`) has no window event loop to drive a modal
     operator.
   - A cleanup step on every exit path removes the timer, clears the status
     text, and resets the progress state.
2. **One sync at a time.** A module-level `SyncProgress` state (Singleton, with
   `reset()` for unregister) records whether a sync is running. While one is
   running, `poll` on `ADD`, `PURGE`, and `ROUTER` returns `False`, with a
   `poll_message_set` explaining why.
3. **Callers start the modal version.** `ROUTER` and `PURGE` call `ADD` with
   `"INVOKE_DEFAULT"` when they were invoked themselves, and with
   `"EXEC_DEFAULT"` from scripts. `call_operator` must accept an execution
   context and count `{"RUNNING_MODAL"}` as success. `PURGE` still purges
   before it starts the download. It is already refused offline.
4. **File loads.** Loading a new file removes modal handlers, but the worker
   keeps running. A `load_pre` handler calls `cancel()` on the running task and
   resets `SyncProgress`. Rows written before then are still valid; nothing is
   applied to the new file.
5. **Unregister** cancels a running task and resets `SyncProgress`, so
   disabling the extension mid-sync leaves nothing behind.

### UI feedback

Each of these reads the same `SyncProgress` (stage, fraction, player name) that
`modal` updates:

- **Status bar:** `context.workspace.status_text_set("Skin Manager: downloading
  Notch's skin… (Esc to cancel)")` during the sync, and
  `status_text_set(None)` when it ends.
- **Panel (Phase 4):** while a sync runs, the panel draws
  `layout.progress(factor=..., type="BAR", text=...)` in place of the *Change
  Skin* button. `modal` calls `tag_redraw()` on 3D Viewport areas after each
  update so the bar moves.
- **Reports:** an INFO report when the skin is applied, or "Skin unchanged",
  and an ERROR report for failures, as now.

`wm.progress_begin` was considered and left out: it replaces the mouse cursor
with a number, which is less clear than the status bar and the panel bar.

### Tests and validation

- `tests/test_background.py`:
  - the result is returned
  - an exception is re-raised on the main thread
  - events arrive in order through `drain()`
  - `cancel()` is visible to the coroutine
  - several tasks run independently
- `tests/test_skin_manager.py`:
  - cancelling at each stage raises `SyncCancelledError` and leaves no rows and
    no new files
  - `stage_progress` increases and ends at 1
- Background Blender: the existing validation script still passes through
  `execute`. Add one check that `poll` refuses a second sync while
  `SyncProgress` reports one running.
- Manual checks in the Blender 5.2 UI (a modal operator needs a window):
  - Change Skin keeps the viewport responsive
  - the status bar text and the panel bar advance and then clear
  - Esc cancels, and nothing is written
  - a second Change Skin is disabled while one runs
  - deleting the rig mid-sync gives the "skin saved" report
  - opening another file mid-sync leaves no stuck status text
  - Purge and Router run the modal version

## Phase 4: Menus and panel

**Done 2026-11-08.** Laid out after the legacy `SKIN_utility_ui.py` panel
and the legacy "regen" and "purge" menus. Decisions and differences:

- Open Decision 1, decided 2026-11-08: the panels get their own sidebar tab,
  `CATEGORY = "Skins"`, like the legacy "Download Skins" tab, and not a
  sub-panel of SACR Config, because the Skin Manager names no rig.
- History, decided 2026-11-08: included as `PanelID.HISTORY` (*Saved Skins*), a
  sub-panel of `MAIN` that is closed by default. Rows are shown newest first, as
  `#index  date  Model`, each with a *Load* button. A row whose file is missing
  has a warning icon and a disabled *Load*.
- Core addition: `SkinManager.saved_skins(name)` (newest first) and
  `skin_path(skin)`. The panel caches the rows by username and the database
  file's modification time, so it does not query SQLite on every redraw.
- `MenuID.EXISTING` (*Player Already Saved*): *Load Saved Skin*, *Check for
  New Skin*, then *Back Up and Purge* and *Purge*. These are the legacy menu's
  three choices plus the legacy purge menu's backup option. Both purge items
  use `PURGE`'s own confirmation dialog.
- `ROUTER` opens the menu only when invoked from the UI (`use_modal`). From a
  script, `Route.PROMPT` runs `ADD`, because a script cannot answer a menu.
- Main panel: *Minecraft Username*, then *Change Skin* (`ROUTER`) and *Player
  Data* (`FILE_OPEN`), then *Options*: *Sync Arm Type* and *Set Rig Name to
  Username* (the legacy labels), shown only when the target has that feature.
  While a background sync runs, a `layout.progress` bar showing
  `sync_progress.text` replaces the buttons. A missing bone shows an error label
  instead of raising.
- Preferences: a *Skin Manager* box with `prompt_to_refresh_player_data` and
  *Import Legacy Player Data* (Open Decision 3: a manual button). The operator
  ID is imported inside `draw()`, because importing `features` while
  `preferences` loads would be circular.

Validated in Blender 5.2.2: the Phase 3 background script, 16/16 offline and
26/26 online. In the UI, with screenshots:

- the menu and both panels are registered, and the sidebar switches to the
  *Skins* tab
- the main panel draws
- the history lists two rows, newest first, marks the missing file, and reuses
  its cache
- `ROUTER` from the UI with a stored player opens the menu
- the progress bar replaces the buttons in the real sidebar during a sync
- the preferences box draws with the import button

Not validated: clicking each menu item and the history *Load* button by hand
(the operators behind them are covered by the Phase 3 and 3b checks), the
import file browser, and a rig with a missing bone.

Still open from Phase 2: importing a legacy file for a player who has already
synced replaces their synced rows. The import button has no warning yet.

Original spec:

- `MenuID.EXISTING`, replacing the legacy "regen" menu: *Load saved skin*,
  *Check for new skin*, *Purge...*. The purge confirmation is `invoke_confirm`
  on `PURGE` rather than a separate menu.
- `PanelID.MAIN`, the *Skin Manager* panel, with the same `poll` as the
  operators. It contains:
  - the `Username` field
  - a *Change Skin* button for `ROUTER`, replaced by the Phase 3b progress
    bar while a sync runs
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

**Done 2026-11-08.** Differences from the spec:

- The docs were reorganised rather than patched. The user pages
  (`extension/index.md`, `skin-manager.md`, `preferences.md`,
  `rig-panels.md`) now describe only what a user sees and does, with
  screenshots taken in Blender 5.2.2 using the player `MamaKitty19`. Code
  details moved under `extension/development/`: `skin-system/` became
  `development/skin-manager/` (new `index.md` overview, plus `service.md`,
  `network.md`, `mojang.md`), `database/` became `development/database/`, and
  `skin-system/index.md` became the user page `extension/skin-manager.md`.
  Old URLs under `extension/skin-system/` and `extension/database/` no longer
  exist.
- `SkinTarget` was already documented in `development/skin-targets.md`
  (Phase 3); it is now linked from the internals overview.
- Two UI fixes found while taking screenshots:
  - `MT_existing` sets `layout.operator_context = "INVOKE_DEFAULT"`.
    `wm.call_menu` ran its items with `EXEC_DEFAULT`, so **Purge** skipped its
    confirmation and **Check for New Skin** blocked Blender instead of running
    in the background.
  - Saved Skins rows split 82/18 with an icon-only load button, so the date
    and model are no longer cut off in the sidebar.
- Checks: compileall, Pyright (0 errors), 138 unit tests, the background
  validation script (26/26 online: registration, offline and empty-name
  refusal, new player, same skin again, rename sync, purge with and without
  backup, legacy import, save and reopen still packed, unregistration), a slim
  skin (`MamaKitty19`) setting `Arm Type` to 1, and UI runs for the panel,
  progress bar, menu, purge confirmation, Saved Skins, and preferences. A
  *changed* skin was not tested live; it is covered by the service tests.

Still open:

- 64x32 (legacy) skins are downloaded and applied without a warning, but
  SACR R7.5 does not support them. The user docs carry a caution.
- Importing a legacy file for a player who already synced replaces their
  rows, with no warning (from Phase 2). The user docs carry a note.

## Open decisions

1. ~~**Panel location.**~~ Decided 2026-11-08: its own *Skins* sidebar tab.
   See Phase 4.
2. ~~**What `SyncName` renames.**~~ Decided 2026-11-08: the object and
   armature data become `"<player> - <target.label>"`, and the collection is
   renamed only if it already ends in `" - <target.label>"`. See Phase 3.
3. **Legacy import:** implemented as a manual button in the preferences
   (Phase 4). Automatic import on first run is not built. Related: whether an
   import should skip players who are already stored (see Phase 2).
4. **Purge backup:** keep it (a folder move is cheap) or drop it, since
   hash-named history makes purging rare? `StorageDir.PLAYER_DATA_PURGED` is
   in place in case it stays.
5. ~~**Blocking `asyncio.run` for 4.0.0.**~~ Decided 2026-11-08: fix it in
   4.0.0 with a background sync and progress feedback. See Phase 3b.
6. **Cancelling a download:** should Esc cancel a running sync? Implemented
   at the default (yes) in Phase 3b. Removing it means dropping the `ESC`
   branch in `SkinAdd.modal`.
