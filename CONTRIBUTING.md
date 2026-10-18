# Contributing to SACR

The extension package lives at the repository root. Keep reusable Python logic in `sacr_core/` or the appropriate feature package, and keep Blender UI and operator code focused on interaction. `lib/` owns the current rig and source assets. Keep `Extra-Scripts/` helpers standalone for interactive enum-property updates.

Rig `.blend` contributions are not accepted through merge requests because binary changes cannot be reliably reviewed or merged. Report rig defects through the [issue tracker](https://gitlab.com/sedaia-designs/advanced-character-rig/-/issues), with the rig and Blender versions and clear reproduction steps.

## Local setup and validation

Use Python 3.13 or newer and [uv](https://docs.astral.sh/uv/) from the repository root:

```sh
uv sync --group dev
uv run python -m compileall -q __init__.py modules.py prefs.py sacr_core sedaia_ui Extra-Scripts
uv run pyright
```

Pyright uses the version-matched `fake-bpy-module-5.2` stubs from the project environment. The stubs support static inspection only. For changes to registration, properties, operators, panels, or rig data, also load the extension in Blender 5.2 or newer and exercise the affected flow. Test standalone scripts on a disposable rig copy when practical. Include the checks performed in the merge request.

The Blender Development for PyCharm plugin uses `blender-workspace.toml`, with the repository root as `source_folder`. Restart Blender after manifest or package layout changes when reload-on-save cannot refresh the extension. Project documentation is at [docs.sakura-sedaia.com](https://docs.sakura-sedaia.com).

Avoid committing `.venv`, Python caches, Blender backups, packaged archives, and local IDE state. Follow [AGENTS.md](AGENTS.md) for detailed repository rules. See [LICENSE](LICENSE) for licensing.
