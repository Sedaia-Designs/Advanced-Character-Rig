# Agent Guidelines

This repository contains the SACR Blender rig and its companion Blender extension in one working layout. Follow this file unless a nested `AGENTS.md` overrides it.

## Layout

- The Blender extension package is at the repository root. `__init__.py` registers it, `modules.py` loads its features, `prefs.py` contains preferences, and `blender_manifest.toml` is its canonical identity and build metadata.
- `sacr_core/` and `sedaia_ui/` contain extension runtime code. Keep feature registration and unregistration explicit and in reverse dependency order.
- `lib/` contains the current rig `.blend` file and source assets. Binary changes require Blender validation; text diffs cannot prove them correct.
- `Extra-Scripts/` contains standalone Blender helpers, primarily for enum properties. Do not fold them into extension runtime without an explicit request.
- `CHANGELOG.md` records rig and extension release notes together. Preserve their separate version numbers.
- `.hidden/` and `Blender-Docs/` are local only; do not modify them unless requested.

## Development

Use the `python-blender-mentoring` skill for Python, Blender API, implementation, testing, and review work. Use `blender-pycharm-workflow` for IDE setup, `edit-changelog` for release notes, and `git-commit` only when asked to commit. Teach meaningful design choices briefly while completing routine edits and checks.

The uv project and extension package are both rooted here. Use Python 3.13 or newer. `fake-bpy-module-5.2` is a development-only stub package used by Pyright and editors; it does not execute Blender code. Run:

```sh
uv sync --group dev
uv run python -m compileall -q __init__.py modules.py prefs.py sacr_core sedaia_ui Extra-Scripts
uv run pyright
```

Run focused tests when present. Validate registration, RNA properties, context-sensitive operators, UI drawing, and rig data inside Blender 5.2 or newer when practical. State which checks passed and which Blender behaviors were not validated. For rig edits, inspect the changed `.blend` in Blender and verify the affected drivers, constraints, properties, assets, and save/reopen behavior.

## Extension rules

- Keep the manifest ID stable unless the user requests migration. Keep its compatibility, permissions, wheels, and build exclusions accurate.
- Keep production code independent of the PyCharm plugin and fake BPY stubs.
- Use Blender APIs and existing module conventions. Keep panels and operators thin; put reusable logic in a suitable library package.
- Report operator failures with `self.report({"ERROR"}, message)` and return `{"CANCELLED"}`. Use `poll()` and context guards where needed.
- Register properties after their `PropertyGroup` classes and remove attached properties on unregister. Do not register custom `bpy.props` directly on `PoseBone`; use bone ID properties.
- Give network requests timeouts, check online access and response validity, and store downloads in extension-local storage. Never print credentials or private asset URLs.
- Avoid broad exception handling that hides programming errors. Prefer atomic file replacement where interrupted writes could corrupt user data.

## Git, assets, and documentation

Inspect `git status --short --branch` before broad edits. Preserve staged, unstaged, and untracked user work. Do not create a commit, push, tag, publish, or release without an explicit request. Do not discard a binary asset or generated backup merely because it is ignored; it may be user work.

Keep changes scoped. Do not edit `.hidden/`, downloaded Blender docs, or unrelated assets. The public documentation is at `docs.sakura-sedaia.com`; update its local checkout only when available and in scope. Keep repository documentation aligned with the observed layout. Do not write session logs unless requested.
