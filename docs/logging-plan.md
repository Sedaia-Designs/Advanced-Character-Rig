# Debug logging plan

Internal planning document for adding debug logging to the extension. Not
scheduled yet. Delete this file once logging ships.

Written 2026-11-07.

## Findings (Blender 5.2)

- **Blender's logger is C-only.** The command-line `--log`, `--log-level`,
  `--log-file`, and `--log-list-categories` flags control Blender's C logger
  (CLOG). `bpy`, `bpy.app`, and `bpy.utils` expose nothing for it, so Python
  messages cannot join those categories.
- **Blender's own Python uses the standard `logging` module.** Loggers such as
  `_bpy_internal.http.downloader` and `_bpy_internal.assets.remote_library` are
  registered at startup.
- **Nothing is configured by default.** The root logger has no handlers and its
  level is WARNING, so `warning()` and above reach the terminal through
  Python's fallback handler, and `debug()` and `info()` are dropped.

There is no need to write a custom logger. Use `logging`.

## Design

- **One logger per module:** `log = logging.getLogger(__name__)`. The extension
  loads as `bl_ext.<repo>.Sakura_Character_Rig`, so every module's logger sits
  under the package logger named `ADDON_PACKAGE`. Setting that one logger's
  level controls the whole extension.
- **`core/` may log.** `logging` is standard library, so the no-`bpy` rule
  holds and tests still run in plain Python. Core never configures logging; it
  only creates loggers and writes messages.
- **Configure only the package logger, in the Blender layer.** Never touch the
  root logger, because that changes output for Blender and every other add-on.
- **Logging is for developers.** Operators still report failures with
  `self.report()`, and UI updates such as download progress still go through
  the Observer callbacks planned for the Skin Manager.
- **No secrets in logs.** Never log credentials or full private asset URLs.
  Follow `core/network.py`, which names only the host in error messages.

## Implementation steps

1. **Preferences toggle.** Add a `debug_logging: BoolProperty` to
   `PREFS_user_preferences`, with an `update` callback that applies it
   immediately.
2. **Setup module.** Add `preferences/logging.py`, or place this in
   `preferences/access.py` if it stays small. It does three things:
   - gets `logging.getLogger(ADDON_PACKAGE)`
   - attaches one `StreamHandler` with a formatter such as
     `"%(levelname)s %(name)s: %(message)s"`, and stops messages also passing
     up to the root logger
   - sets the level to DEBUG when the toggle is on or `bpy.app.debug_python` is
     set (`--debug-python`), and to WARNING otherwise
3. **Register and unregister.** Apply the setup when `preferences` registers.
   In `unregister()`, remove the handler. Otherwise every add-on reload adds
   another handler and each message prints once per reload.
4. **Optional log file.** A second preference for a file path, using a
   `FileHandler` in extension storage
   (`storage_dir()` / `sacr.log`). Rotate it or cap its size if it is added.
5. **Add log calls where they help debugging.** First candidates:
   - `core/network.py`: request start, finish, and failure, by host only
   - `core/databases/schema.py`: schema creation and version checks
   - the Skin Manager service: sync decisions, such as reusing a stored skin
     versus downloading a new one
6. **Tests.** Use `unittest`'s `assertLogs` to check key messages in core tests.
   Check in Blender that toggling the preference takes effect at once, and that
   reloading the add-on does not duplicate output.
7. **Document it.** Add a section to the docs site's
   `development/architecture.md` covering how to enable debug output and how
   modules get their logger.

## Open decisions

1. **Toggle location:** a visible preference, or only `--debug-python`?
2. **Log file:** wanted, or terminal output only?
3. **Format:** include timestamps, or keep lines short for the terminal?
