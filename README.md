![](.assets/sacr_basic.png)

This repository contains the SACR Blender rig and its companion Blender extension. The extension source and manifest are at the repository root; the current rig and its assets are in [`lib/`](lib/). [`scripts/`](scripts/) contains standalone scripts used to set custom enum properties on newer rigs.


| Path                                                          | Contents                                                                  |
|---------------------------------------------------------------|---------------------------------------------------------------------------|
| `__init__.py`, `modules.py`, `prefs.py`, `core/`, `features/` | Blender extension runtime                                                 |
| `blender_manifest.toml`                                       | Extension identity, compatibility, permissions, and packaging             |
| `lib/`                                                        | Current SACR `.blend` file and source assets                              |
| `scripts/`                                                    | Interactive Blender & Repository helpers, separate from extension runtime |
| `docs/wiki/`                                                  | Generated GitHub Wiki pages for the extension API                         |
| `CHANGELOG.md`                                                | Rig and extension release notes                                           |

The manifest currently requires Blender 5.2 or newer. Install a packaged extension through **Edit > Preferences > Get Extensions > Install from Disk**, or use the repository's Blender Development for PyCharm workflow. Open `lib/SACR.R7.5.0.blend` to work on the current rig. See [SACR documentation](https://docs.sakura-sedaia.com) for usage and compatibility guidance.

## Development

Install [uv](https://docs.astral.sh/uv/) and run from the repository root:

```sh
uv sync --group dev
uv run python -m compileall -q __init__.py modules.py prefs.py core features scripts
uv run pyright
uv run python scripts/generate_api_docs.py
```

The API generator uses import stand-ins for Blender so it runs outside Blender. It writes a [GitHub Wiki export](docs/wiki/Home.md) with `Home.md`, `_Sidebar.md`, flat API pages, and the [v1 skin API map](features/skins/README.md). Copy the contents of `docs/wiki/` into the wiki repository to publish them.

`fake-bpy-module-5.2` supplies Blender 5.2 API stubs to Pyright and the IDE. It is a development-only type package, not Blender itself. The Pyright check catches type and API issues against those stubs; validate registration, operators, and UI behavior in Blender. The shared `blender-workspace.toml` points the PyCharm plugin at the root package and current rig.

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and validation guidance, and [AGENTS.md](AGENTS.md) for repository rules.

## License

See [LICENSE](LICENSE).
