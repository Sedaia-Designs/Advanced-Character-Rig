# Contributing to SACR

Thanks for helping improve the Sakura Advanced Character Rig (SACR), Sakura Rig
Utilities, or the repository's Blender helper scripts. This monorepo contains
three independent components, so begin by choosing the component that owns the
change:

| Component | Use it for |
| --- | --- |
| `Character-Rig/` | Rig `.blend` files and rig assets |
| `Extension/` | The Sakura Rig Utilities Blender Extension and its tests |
| `Extra-Scripts/` | Standalone, interactive Blender helpers |

Do not move code between these components just because they share a repository.
In particular, an extra script is not extension runtime code unless the change
explicitly calls for that promotion.

## SACR rig files are not accepted contributions

Do not submit edits, additions, replacements, or other contributions to SACR
`.blend` files. Blender files are binary assets, and the Git and Blender
workflow used by this project does not support reliably reviewing, merging, or
integrating contributed rig-file changes.

Please use an issue to report a rig defect or propose an improvement instead.
Include the SACR version, Blender version, rig variant, and clear reproduction
or use-case details so the maintainers can evaluate it.

## Before you start

1. Read the root [README](README.md) and the relevant guidance at
   [docs.sakura-sedaia.com](https://docs.sakura-sedaia.com).
2. Search existing [issues](https://gitlab.com/sedaia-designs/advanced-character-rig/-/issues)
   before opening a new report or beginning substantial work.
3. For a feature or behavior change, open an issue first when the intended
   design is unclear or could affect compatibility.
4. Keep each merge request focused. Do not include unrelated cleanup, generated
   files, local Blender state, or downloaded assets.

Please follow the applicable component license:
[`Character-Rig/LICENSE`](Character-Rig/LICENSE) for the rig and assets, and
[`Extension/LICENSE`](Extension/LICENSE) for the extension.

## Documentation

[docs.sakura-sedaia.com](https://docs.sakura-sedaia.com) is the canonical home
for SACR project documentation, including rig usage, extension workflows,
compatibility, and release guidance. Update the hosted documentation whenever a
contribution changes user-facing behavior, setup, or supported workflows.

Repository documentation is limited to source layout, development setup, and
contribution practices. Do not treat a component README as the authoritative
source for user-facing project documentation.

For changes to Sakura Rig Utilities documentation, edit the local Sedaia Docs
source at `/Users/Sakura/Documents/WebstormProjects/sakura-project-documentation/src/content/docs/sakura-rig-utilities`.
Add user-facing contribution guidance to that documentation route as well as
updating this repository guide when its development workflow changes.

## Extension development setup

The Python project is at the repository root; the extension source is
`Extension/src`. You need:

- Blender 4.2 or newer for extension installation and interactive validation.
- [uv](https://docs.astral.sh/uv/).
- Python 3.13 or newer, as specified by `pyproject.toml`.

From the repository root, create the development environment and run the
automated checks:

```shell
uv sync --group dev
uv run python -m compileall Extension/src
uv run python -m unittest discover -s Extension/tests -v
```

Use the shared [Launch Blender configuration](.run/Launch%20Blender.run.xml)
when developing interactively in PyCharm, or configure your own Blender launch
workflow so that it loads the source in `Extension/src`.

Unit tests deliberately isolate logic that can run without Blender. For changes
to registration, `bpy.props`, operators, UI panels, or context-sensitive code,
also test in Blender: enable or reload the extension, exercise the affected
workflow, and confirm that reloading does not leave stale UI, properties, or
errors behind.

## IDE setup

Both supported IDE workflows use the root uv environment for Python tooling and
the extension package at `Extension/src`. The bundled `fake-bpy-module` package
provides editor-facing Blender API stubs; it supports completion and static
inspection but cannot validate Blender runtime behavior.

### PyCharm with Blender Development for PyCharm

This project uses Sakura Sedaia's
[Blender Development for PyCharm](https://www.sakura-sedaia.com/projects/blender-development)
plugin. It is not yet published on the JetBrains Marketplace, so obtain its
plugin archive from the project page and install it manually:

1. In PyCharm, open **Settings/Preferences > Plugins**.
2. Select the gear menu, choose **Install Plugin from Disk…**, select the
   downloaded plugin archive, and restart PyCharm when prompted.
3. Open this repository as the project and select its uv-managed Python
   interpreter.
4. In the Blender Development plugin settings, choose a supported Blender
   installation (Blender 4.2 or newer) and configure `Extension/src` as the
   extension source folder. This directory contains both `__init__.py` and
   `blender_manifest.toml`.
5. Run the shared **Launch Blender** configuration in
   [`.run/`](.run/) to test the extension. Use reload-on-save for ordinary
   edits; restart Blender after manifest, permissions, package-layout, or
   registration changes that do not reload cleanly.

The manifest ID in `Extension/src/blender_manifest.toml` is the extension's
canonical identity. Do not change it, the selected source folder, or the
plugin's generated link configuration to work around an extension error.

### Visual Studio Code with Blender Development

1. pen the root-level [`vs-code.code-workspace`](vs-code.code-workspace) file
   with **File > Open Workspace from File…**. It opens this monorepo at the
   same root level used by the shared PyCharm configuration. Do not open an
   individual component folder instead.
2. Install the extensions prompted by the workspace recommendations, including
   the Microsoft Python/Pylance tools and
   [Blender Development by Jacques Lucke](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development).
   The workspace already configures the root `.venv` interpreter, Pylance paths,
   `Extension/src` as the Blender Development source directory, and reload on
   save.
3. Open a new terminal panel and run `uv sync --group dev` from the repository root to create the `.venv`
   environment used by the workspace.
4. Open the Command Palette (ctrl shift p) and run **Blender: Start**. Select a Blender 4.2+
   executable when prompted.
5. Use **Blender: Reload Addons** when you need a manual reload.

For autocomplete-path troubleshooting or a separate generated-stubs workflow,
follow the [fake-bpy-module VS Code setup guide](https://github.com/nutti/fake-bpy-module/blob/main/docs/setup_visual_studio_code.md).
Do not override the workspace source-directory setting with the repository root
or another component directory: `Extension/src` contains the extension package
and its manifest. Put personal VS Code settings, launch configurations, and
other machine-specific changes in `.vscode/`; it is ignored by Git and will not
be transmitted to the repository. Keep `vs-code.code-workspace` for settings
that should be shared by every contributor.

## Making changes

### Blender extension

- Keep runtime code under `Extension/src` and keep the manifest at
  `Extension/src/blender_manifest.toml` accurate.
- Add new feature packages to `Extension/src/loader.py`; every package needs
  explicit `register()` and `unregister()` functions.
- Keep panels and operators thin. Put reusable file, network, and business
  logic in the appropriate `lib/` package.
- Use existing extension ID helpers for Blender operator, panel, menu, and UI
  list IDs.
- Network requests need timeouts and clear error handling. Store user data and
  downloads in the extension's configured data location, not the source tree.
- Add or update focused tests under `Extension/tests` for reusable logic.

### Rig files and assets

- SACR `.blend` file contributions are not accepted; see
  [SACR rig files are not accepted contributions](#sacr-rig-files-are-not-accepted-contributions).
- Do not modify image assets or release archives unless the work has been
  explicitly coordinated with the maintainers.
- Preserve historical builds and follow the hosted release guidance for any
  approved asset work.

### Extra scripts

- Keep scripts self-contained and clearly targeted at their Blender task.
- Compile changed Python files before submitting. When practical, test them on
  a disposable copy of the intended Blender file.

## Validation and documentation

Run the checks relevant to your change before opening a merge request. State
which commands you ran and what you verified in Blender; distinguish automated
checks from interactive Blender validation. Update user-facing documentation
at [docs.sakura-sedaia.com](https://docs.sakura-sedaia.com) when behavior,
setup, compatibility, or workflows change.

Avoid committing `__pycache__`, virtual environments, packaged archives,
downloaded assets, local Blender state, or operating-system metadata. The
repository `.gitignore` lists the common generated files.

## Submit a merge request

1. Rebase or otherwise resolve conflicts with the target branch as needed.
2. Write a concise summary of the behavior change and its motivation.
3. Link the relevant issue, if there is one.
4. List automated checks and manual Blender validation performed, including the
   Blender version where relevant.
5. Call out compatibility effects, migration needs, or remaining limitations.

For repository-wide standards—including naming, Blender lifecycle, state
management, error handling, and validation—follow [`AGENTS.md`](AGENTS.md).
