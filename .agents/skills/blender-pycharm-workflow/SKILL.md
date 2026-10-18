---
name: blender-pycharm-workflow
description: Configure, use, or troubleshoot this Blender src with the Blender Development for PyCharm plugin. Use when working on PyCharm project setup, Blender installation selection, src source-folder or repository configuration, version-matched bpy stubs, the shared Launch Blender run configuration, reload-on-save, enabling the manifest module, or distinguishing IDE issues from src runtime defects.
---

# Blender PyCharm Workflow

Use Blender Development for PyCharm as development tooling around this repository. Do not introduce a runtime dependency on the IDE plugin.

## Inspect Before Changing

1. Read `AGENTS.md`, `pyproject.toml`, `blender_manifest.toml`, and `blender-workspace.toml`.
2. Inspect the current plugin configuration or error evidence before editing project metadata.
3. Preserve unrelated workspace configuration, interpreter, manifest, and source changes.
4. Prefer fixing extension code or metadata when the plugin is correctly exposing a real Blender error.

## Keep Project Identity Aligned

- Configure the repository root as the extension source folder; it contains both `__init__.py` and `blender_manifest.toml`.
- Treat the manifest `id` as the canonical extension identity. The plugin may enable it through a module name shaped like `bl_ext.<repository>.<manifest-id>`.
- Treat a symlink name as development configuration, not as the canonical manifest ID.
- When the extension fails to reload after an ID, repository, source-folder, or symlink change, check for a stale enabled module before changing source code.
- Keep repository-specific absolute paths out of shared extension code and manifest metadata.

## Use the Python Environment Correctly

- Use the project interpreter declared by PyCharm and reflected in the uv project.
- Keep Blender API stubs version-matched to the intended Blender release when possible.
- Use stubs for completion and static inspection only. They cannot validate Blender context, registration, RNA behavior, or UI rendering.
- Do not add the IDE plugin or its bundled runtime as an extension dependency.

## Run and Debug

- Use the Blender Development plugin launch workflow for interactive extension behavior.
- Confirm the selected Blender installation meets `blender_version_min`.
- Use reload-on-save for ordinary iteration, but restart Blender after changes to manifest identity, permissions, package structure, or stubborn registration state.
- For a reload failure, distinguish:
  1. configuration failure: source folder, installation, repository, or module identity;
  2. import/registration failure: traceback while enabling or reloading;
  3. behavior failure: extension loads but an operator, panel, or workflow is wrong.
- Capture the Blender traceback or operator report before making speculative changes.

## Validate at the Right Layer

- Run `python -m compileall -q __init__.py modules.py prefs.py sacr_core sedaia_ui` for Python syntax and import compilation.
- Run repository unit tests for logic isolated from Blender.
- Inspect TOML structure and permissions after manifest edits.
- Exercise registration, panels, context-sensitive operators, and reload behavior inside Blender.
- State clearly when only stub-backed or non-Blender validation was possible.

## Handle Plugin Defects Across Repositories

If evidence points to Blender Development for PyCharm rather than this extension:

1. Record a minimal reproduction using this repository's source-folder, manifest-ID, and run configuration facts.
2. Inspect `/Users/Sakura/Documents/IdeaProjects/blender_pycharm` only when the user asks to diagnose or change the companion plugin.
3. Read that repository's `AGENTS.md` before making any companion-repository changes.
4. Keep extension and IDE-plugin fixes separate; do not edit both merely to mask one side's defect.
5. Do not commit, push, publish, or release either repository without explicit authorization.
