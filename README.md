# Sakura Advanced Character Rig

Sakura Advanced Character Rig (SACR) is a Blender rig for Minecraft-style
character renders. This repository brings together the rig and its assets, the
Sakura Rig Utilities Blender Extension, and reusable one-off Blender scripts.
Each component has its own release lifecycle, but they are developed and
maintained together here.

## What's in this repository?

| Component                          | Purpose                                                   | Start here                                              |
|------------------------------------|-----------------------------------------------------------|---------------------------------------------------------|
| [`Character-Rig/`](Character-Rig/) | SACR `.blend` releases and source assets                  | [Project documentation](https://docs.sakura-sedaia.com) |
| [`Extension/`](Extension/)         | Sakura Rig Utilities extension source and automated tests | [Project documentation](https://docs.sakura-sedaia.com) |
| [`Extra-Scripts/`](Extra-Scripts/) | Standalone helpers for interactive, one-off Blender tasks | The script that matches the task                        |

The rig files, extension, and scripts are intentionally separate. A helper
script may rely on the current Blender file and is not automatically part of
the extension runtime.

Historical branches and tags imported from the former rig and extension
repositories use the `rig/` and `extension/` namespaces. Stable releases,
experimental builds, and older files remain available for long-term access.

## Use SACR

1. Browse [`Character-Rig/Versions/`](Character-Rig/Versions/) and select the
   SACR revision you need. Prefer the newest patch release for that revision.
2. Open the chosen `.blend` file directly in Blender, or append/link the rig
   into another project.
3. Check the version directory for release notes and supporting files.

Older rigs can depend on the Blender version they were made with and may not
work correctly in current Blender. Development builds are retained for testing
and preservation; they are not production releases. See the project
documentation for version naming, experimental builds, and Blender-version
compatibility.

## Sakura Rig Utilities extension

Sakura Rig Utilities (currently presented in Blender as **Sedaia Rig
Interfaces**) adds SACR-specific controls and management workflows, including
rig and skin tools. It is in active, early development, so some planned tools
may be incomplete.

It requires Blender 4.2 or newer. To install a released extension package:

1. Download the latest package from the
   [GitLab releases page](https://gitlab.com/sedaia-designs/advanced-character-rig/-/releases)
   or the [Blender Extensions platform](https://extensions.blender.org/add-ons/sakura-rig-interfaces/).
2. In Blender, open **Edit > Preferences > Extensions**.
3. Open the menu in the upper-right, choose **Install from Disk…**, and select
   the downloaded `.zip`.
4. Enable the extension, then open the 3D Viewport sidebar with, and find
   the **Sedaia** tab.

Sakura Rig Utilities is intended to become the preferred way to discover,
download, and import SACR rigs from Blender. Until that workflow is complete,
download rig files and assets directly from this repository or its releases.

## Documentation

The canonical home for SACR documentation—including rig usage, extension
workflows, compatibility, and release guidance—is
[docs.sakura-sedaia.com](https://docs.sakura-sedaia.com). Repository files
describe the source layout and contribution workflow; they do not replace the
hosted project documentation.

## Development

> [!NOTE]
> It is recommended to use either Visual Studio Code or PyCharm using their associated Blender Development plugins. 
> - For Visual Studio Code, install the [Blender Development]([https://marketplace.visualstudio.com/items?itemName=BlenderFoundation.blender-development](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development)) extension by Jacques Lucke. 
> - For PyCharm, install the [Blender Development](https://plugins.jetbrains.com/plugin/18389-blender-development) plugin by Sakura Sedaia.

The Python development environment is defined by the root
[`pyproject.toml`](pyproject.toml); the extension source lives in `Extension/src`.
Install [uv](https://docs.astral.sh/uv/) and a Python version compatible with
the project (currently Python 3.13 or newer), then run from the repository
root:

```shell
uv sync --group dev
uv run python -m compileall Extension/src
uv run python -m unittest discover -s Extension/tests -v
```

The syntax check and unit tests exercise reusable Python logic outside Blender.
They do not prove Blender registration, UI drawing, or context-sensitive
behavior. Validate those changes interactively in a supported Blender version.
The shared PyCharm run configurations are in [`.run/`](.run/).

For the project layout, coding conventions, Blender extension lifecycle, and
component-specific validation expectations, read [`AGENTS.md`](AGENTS.md).

## Contributing and support

Contributions, maintenance work, compatibility fixes, bug reports, and feature
requests are welcome when they comply with the applicable component license.
Please use the [issue tracker](https://gitlab.com/sedaia-designs/advanced-character-rig/-/issues)
for reproducible bugs and proposals. Include the SACR version, Blender version,
rig variant, and reproduction steps when reporting a rig or extension issue.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a merge request. It
covers local setup, validation, scope boundaries, and review expectations.

Community discussion is also available on [Discord](https://discord.gg/Qk4pfbG7Pf)
and [Fluxer](https://fluxer.gg/M9gYmCdr).

## License

This Repository and all content featured within it are licensed under the GNU/GPL V3. Consult
[`LICENSE`](LICENSE) for more information.

## AI Usage

This project was made in tandem with AI tools. AI was used to help write unit tests, documentation, code analysis and automate tasks. Very little of the actual source code was written using an LLM.