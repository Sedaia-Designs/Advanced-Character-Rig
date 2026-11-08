# Codebase audit, 2026-11-07

A snapshot of the codebase after the day's Skin Manager work (rig targets, R7.5
constants, Skin Manager IDs, and the implementation and logging plans). It is
based only on code read during that work, not a full review. Tick items off or
delete this file once its findings are handled.

**Summary:** the architecture is ahead of the features. The `core/`
foundations are solid; the main gap is the Skin Manager itself.

## Strengths

- **The `core/` layer.** The network, SQLite, schema, and skin database code
  is well tested and has no `bpy` imports, and each module names the design
  pattern it follows. The network code is careful about security: HTTPS only,
  size limits, timeouts, atomic downloads, and error messages that name only
  the host.
- **Stable names.** Every idname comes from an explicit `StrEnum` value built
  through `core.ids.ID`, so "don't break keymaps" is enforced by the code
  rather than by memory.
- **Rig-agnostic Skin Manager.** R7.5 rig names live once in
  `features/SACR_R7_UI3/constants.py`, and the Skin Manager names no rig.
  Supporting another rig is one `SkinTarget` in that rig's feature.
- **Clean checks and up-to-date docs.** 84 tests and Pyright pass with no
  errors. `AGENTS.md`, `docs/`, and the docs site match the current layout.

## Behind

- [ ] **The Skin Manager has no user-facing function yet.** It has storage,
  networking, constants, and a router that reads the username and stops. The
  legacy tool can still do more. See `docs/skin-manager-plan.md`, Phases 1–3.
- [ ] **The changelog is ahead of the code.** It lists `skin_router` and
  `skin_add` as added, but both are stubs. It dates the unreleased 4.0.0 as
  2026-10-18. It says skin settings moved to the scene, but they are on the
  `PythonConfig.Skin` bone. Covered by the plan's Phase 5.
- [ ] **Untested in Blender.** The full extension was not loaded in Blender
  during this work. Registration, panel drawing, and the router's `poll` on a
  real rig still need checking. (Enum-key lookups and `SKIN_TARGET.matches`
  were checked against `lib/SACR.R7.5.0.blend` in Blender 5.2.)

## Cleanup

- [x] **Dead rig-module auto-import in `modules.py`.** It scanned a `rig_ui/`
  folder that no longer exists, and its path building looked broken. The user
  commented it out instead of deleting it, with a TODO, as a starting point for
  future **Rig Plugins** that let other rigs use SACR's utilities. If that is
  built:
  - Fix the path building first. `iter_submodule_names` mixes `/` and `.`
    separators, so nested packages would not import.
  - Consider the `core.skin_targets` registry as the model. A plugin rig would
    register its own `SkinTarget`, so it gets the Skin Manager with no other
    changes.
  - The imports it needs (`import_module`, `pkgutil`, `Path`) are still at the
    top of `modules.py`, unused for now. Compile and Pyright pass with them.
- [ ] **The R7.5 UI is older than the current rules:**
  - Most property paths (`'["Arm Type"]'`) and node names are still literal
    strings, and `ui/enums.py` uses a dict where the rules call for enums.
  - Its namespace, `RIG_ID_GROUP`, lives in `ui/__init__.py` instead of the
    feature's `constants.py`.
  - Many docstrings are filler ("Perform toggle collection.").
  - The `draw()` "docstring" in `panels/main.py` comes after a comment line, so
    Python does not treat it as a docstring.
- [ ] **Some shared operators crash instead of reporting:**
  - `IMAGE_pack` and `IMAGE_reload` look up `bpy.data.images[self.path]`
    without a guard. A wrong name raises a traceback instead of calling
    `self.report({"ERROR"}, ...)`, as `AGENTS.md` requires.
  - `RIGS_set_name` falls back to `context.asset` when renaming the collection
    fails, which looks unrelated to the failure.
  - `FILE_DELETE` is declared but has no operator.

## Repository state

- [ ] **Unpushed work.** `main` was 31 commits ahead of `origin/main` at the
  time of the audit, so a lot of history exists only on this machine.
- [ ] **Docs repo uncommitted.** `sedaia-web-platform` still holds today's
  pages, mixed in with other uncommitted work.

## Next steps

1. Phases 1–3 of `docs/skin-manager-plan.md` (Mojang adapter, Skin Manager
   service, operators), so the Skin Manager becomes usable.
2. A small cleanup pass on the shared operators. It is low-risk and can happen
   at any time.
3. Load the extension in Blender 5.2 and check registration and the panels.
