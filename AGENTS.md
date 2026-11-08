# Agent Guidelines

This repository contains the Sakura character rig and its companion Blender extension in one project. The rig (formerly SACR) and the extension (formerly the SR GUI) are being merged, so expect names and namespaces to change. Follow this file unless a nested `AGENTS.md` overrides it.

## Layout

- The Blender extension package is at the repository root. `__init__.py` registers it, `modules.py` loads its packages in dependency order, `preferences/` contains the add-on preferences and reads the extension ID from the manifest through `core/manifest.py`, and `blender_manifest.toml` is its canonical identity and build metadata.
- `core/` contains Blender-agnostic Python. It must never import `bpy`.
- One package per Blender type, each built on top of `core/`:
  - `operators/` for operators
  - `panels/` for panels
  - `menus/` for menus
  - and likewise for other types, such as UI lists or property groups, when they are added.
- `features/` contains complete features, one subpackage each. Examples: a full rig UI, skin management, and rig management. See "Feature packages" below.
- The only supported rig UI is SACR R7.5 (`features/SACR_R7_UI3/`). Older SACR releases use the legacy SR GUI download; do not reintroduce their UIs.
- `.legacy/sedaia_utils.py` and `.legacy/SKIN_utility_ui.py` are legacy code. They are kept as working reference for the skin tool rewrite, which gets a new backend in `core/` and `features/`.
  - They are orphaned: not registered, not imported, excluded from the extension build, and skipped by Pyright and the compile check.
  - Do not edit, refactor, fix, or migrate them. Read them for behaviour, and implement the rewrite fresh.
  - Do not import from them or add code to `.legacy/`.
  - Delete both, and the `.legacy/` folder, once the rewrite replaces them.
- `lib/` contains the current rig `.blend` file and source assets. Binary changes require Blender validation; text diffs cannot prove them correct.
- `.scripts/` contains standalone Blender helpers (the enumerator scripts) and `generate_api_docs.py`. Do not fold them into extension runtime without an explicit request.
- `CHANGELOG.md` records rig and extension release notes together. Preserve their separate version numbers.
- `.hidden/` and `Blender-Docs/` are local only when present; do not modify them unless requested.

## Organization rules

### Core is Blender-agnostic

- `core/` holds reusable logic: data parsing, network lookups, file reads and writes, and ID construction (`core/ids.py`).
- Core never controls Blender. Pass Blender-derived values, such as paths from `bpy.utils.extension_path_user`, into core functions as arguments instead of resolving them inside `core/`.
- The core logic behind every operator must be testable in a plain Python environment with no `bpy`.
- Exception: logic that cannot work without `bpy`, such as packing an image (`pack_img`), does not belong in core.

### Blender code lives in operators

- Code that requires `bpy` belongs inside the operator that uses it unless that is impossible. Panel `draw()` and menu `draw()` code are the expected exceptions.
- Keep operators thin. They gather context, call core, apply the result to Blender, and report errors.
- Do not create shared `bpy` helper modules to avoid duplicating a few lines. Only factor out Blender code when several types truly need the same behaviour, and say why in the module docstring.

### Feature packages

- A complete feature lives in `features/<feature>/`. Examples: `features/skins/`, `features/rigs/`, or one rig's full UI.
- Inside a feature, follow the same type-package rules as the root: an `operators/`, `panels/`, or `menus/` subpackage only where the feature needs that type. Each subpackage has its own registration layer and `constants.py`.
- The feature's `__init__.py` registers its subpackages in dependency order, and the feature is added to `modules.py` like any other package.
- Give each feature its own `NAMESPACE` so its idnames cannot collide with other features.
- Feature logic that doesn't need Blender still belongs in `core/`, so it stays testable without `bpy`.
- The root type packages (`operators/`, `panels/`, `menus/`) hold only shared classes that are not owned by one feature. If a class belongs to a single feature, put it in that feature.

### Every type package has a registration layer

Follow the convention in `operators/`:

- Each module ends with a `classes = (...)` tuple of the Blender classes it defines, in registration order.
- The package `__init__.py` imports each module's `classes`, flattens them into one tuple (`*file_classes, *image_classes, ...`), registers them in order, and unregisters them in reverse.
- Add the package to `modules.py` using the existing `reload` pattern, in dependency order.
- Register properties after their `PropertyGroup` classes and remove attached properties on unregister.

### Every type package has a constants module

- Each package has a `constants.py` that declares the ID name of every class it registers. Examples: `OperatorID` and `MenuID` in `operators/constants.py`.
- IDs are `StrEnum` members with explicit values built from `core.ids.ID`, for example `SKIN_LOAD = ID("skin_load").operator_for(NAMESPACE)`. Never use `auto()`: renaming a member must not change a public idname.
- Classes take their `bl_idname` from the enum, and UI code references members, never literal ID strings.
- `core.ids.ID_PREFIX` and each package's `NAMESPACE` form the public idnames. Changing either breaks user keymaps and scripts; flag it and record it in `CHANGELOG.md`.

### Prefer enums over dictionaries for configuration

- Use `StrEnum` (or `IntEnum`) with explicit, hardcoded values for fixed configuration such as IDs, URLs, bone names, and property keys.
- Use dictionaries only for data that is genuinely dynamic, such as parsed JSON or user data.

## Development

Use the `python-blender-mentoring` skill for Python, Blender API, implementation, testing, and review work. Use `blender-pycharm-workflow` for IDE setup, `edit-changelog` for release notes, and `git-commit` only when asked to commit. Teach meaningful design choices briefly while completing routine edits and checks.

The uv project and extension package are both rooted here. Use Python 3.13 or newer. `fake-bpy-module-5.2` is a development-only stub package used by Pyright and editors; it does not execute Blender code. Run:

```sh
uv sync --group dev
uv run python -m compileall -q __init__.py modules.py preferences core operators panels features tests
uv run pyright
```

Test core logic outside Blender, and never import `bpy` or the fake stubs in core tests. Run focused tests when present. Validate registration, RNA properties, context-sensitive operators, UI drawing, and rig data inside Blender 5.2 or newer when practical. State which checks passed and which Blender behaviours were not validated. For rig edits, inspect the changed `.blend` in Blender and verify the affected drivers, constraints, properties, assets, and save/reopen behaviour.

## Extension rules

- Keep the manifest ID stable unless the user requests migration. Keep its compatibility, permissions, wheels, and build exclusions accurate.
- Keep production code independent of the PyCharm plugin and fake BPY stubs.
- Report operator failures with `self.report({"ERROR"}, message)` and return `{"CANCELLED"}`. Use `poll()` and context guards where needed.
- Do not register custom `bpy.props` directly on `PoseBone`; use bone ID properties.
- Give network requests timeouts, check online access and response validity, and store downloads in extension-local storage. Never print credentials or private asset URLs.
- Avoid broad exception handling that hides programming errors. Prefer atomic file replacement where interrupted writes could corrupt user data.

## Git, assets, and documentation

Inspect `git status --short --branch` before broad edits. Preserve staged, unstaged, and untracked user work. Do not create a commit, push, tag, publish, or release without an explicit request. Do not discard a binary asset or generated backup merely because it is ignored; it may be user work.

Keep changes scoped. Do not edit `.hidden/`, downloaded Blender docs, or unrelated assets. The public documentation is at `docs.sakura-sedaia.com`; update its local checkout only when available and in scope. Keep repository documentation aligned with the observed layout. Do not write session logs unless requested.
