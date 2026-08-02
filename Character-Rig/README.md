# Sakura Advanced Character Rig

Sakura Advanced Character Rig (SACR) is a Blender rig for creating Minecraft-style character renders. It is designed to provide a broad set of posing and customization features while keeping the rig, drivers, and meshes efficient enough for practical scene and render performance.

This directory is the canonical home for SACR rig files and supporting assets within the [SACR monorepo](https://gitlab.com/sedaia-designs/advanced-character-rig). Releases and development history from the former standalone and version-specific branches are retained in the monorepo under namespaced refs.

## Future plans

This repository will remain active and continue to receive new Blender rig files and supporting assets. In the future, however, Sakura Rig Utilities will become the recommended way to discover, download, and import SACR rigs directly into Blender.

Sakura Rig Utilities and the website services that support it are still under development, so this workflow is not yet fully available. Until it is ready, rigs and assets can continue to be downloaded directly from this repository.

## Repository contents

- `Versions/` contains SACR releases, historical development builds, and the earlier Sakura Advanced Minecraft Rig (SAMR).
- `Assets/` contains supporting resources, including the superslim skin template in PNG and Blockbench formats.
- Version-specific folders may include standard, lite, styled, or development variants alongside their changelogs.
- [`FAQ.md`](FAQ.md) covers release scheduling, feature requests, experimental version naming, and Blender compatibility.

Historical files are retained for long-term access. Older rigs may depend on the Blender version in which they were created and are not guaranteed to work correctly in current Blender releases.

## Using a rig

1. Open `Versions/` and choose the SACR revision you need.
2. Prefer the latest patch release within that revision unless you specifically need an older build.
3. Open the `.blend` file directly in Blender, or append/link the rig into another project.
4. Check the version folder for a changelog or other release-specific notes.

Development files are included for preservation and testing. They may be incomplete or unstable and should not be treated as production releases.

## Project history

SACR began as a lightweight, performance-conscious rig for Minecraft character artwork in Blender. Revision 7 introduced improved shape keys, optimized meshes and drivers, restored full rig bone shapes, and a rebuilt facial rig mesh.

The former SACR Experimental repository was later merged into the primary project. Stable releases, experimental builds, and supporting assets are now being organized together by major version so the project's development history remains accessible without relying on separate branches.

## Support and contributions

There is no fixed release schedule; SACR is maintained as a passion project. Bug reports and feature requests can be submitted through the repository's issue tracker or discussed in [Sakura's Discord server](https://discord.gg/Qk4pfbG7Pf) or [Fluxer Server](https://fluxer.gg/M9gYmCdr). Feature requests are welcome, but inclusion is not guaranteed.

Community maintenance, modifications, and compatibility work are welcome when permitted by the applicable release license. When reporting a problem, include the SACR version, Blender version, rig variant, and steps needed to reproduce it.
