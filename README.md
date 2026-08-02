# Sakura Advanced Character Rig

This monorepo contains the Sakura Advanced Character Rig (SACR), the Sakura Rig Utilities Blender Extension, and supporting development scripts.

## Projects

- [`Character-Rig/`](Character-Rig/) contains released and development Blender rig files, source assets, and rig documentation.
- [`Extension/`](Extension/) contains the Blender Extension runtime, tests, manifest, and Python tooling.
- [`Extra-Scripts/`](Extra-Scripts/) contains standalone Blender helpers used for one-off rig development tasks.

The rig and extension retain their independent release lifecycles. Historical branches and tags imported from their former repositories are namespaced with `rig/` and `extension/`.

## Development

Python and extension commands run from `Extension/`:

```shell
cd Extension
uv run python -m compileall src
uv run python -m unittest discover -s tests -v
```

Interactive Blender development uses the shared run configurations in [`.run/`](.run/). See [`AGENTS.md`](AGENTS.md) for workspace conventions and each component README for usage and release details.

## Repository

- Issues: <https://gitlab.com/sedaia-designs/advanced-character-rig/-/issues>
- Releases: <https://gitlab.com/sedaia-designs/advanced-character-rig/-/releases>
