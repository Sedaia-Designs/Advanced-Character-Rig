# Minecraft skin feature

`features.skins` downloads Minecraft player textures, keeps a per-player
history in extension-local storage, and applies a selected skin to a SACR rig.
It is registered by `modules.py` after preferences and the rig interfaces.

## Map

```text
modules.py
    └── features.skins.register()
            ├── operators.py       Blender actions and workflow routing
            ├── menus.py           refresh and purge confirmation menus
            └── panel.py           Viewport sidebar panel

panel / menus
    └── operators
            ├── context.py         finds the supported active rig
            ├── repository.py      player-data paths and JSON persistence
            ├── service.py         Mojang requests and texture downloads
            └── core/              shared Blender, network, and storage helpers
```

`constants.py` is the shared boundary for stable Blender IDs, the metadata
bone name, Mojang endpoints, and the request timeout. `models.py` contains the
immutable value objects produced while parsing the remote profile; persisted
data remains a JSON-compatible dictionary rather than these dataclasses.

## Blender entry points

The module registers these classes in this order:

1. `SKIN_router`, `SKIN_get`, `SKIN_add`, `SKIN_load`, and `SKIN_purge`
2. `SKIN_menu_purge` and `SKIN_menu_regen`
3. `SEDAIA_SKIN_PT_ui_skinUtility`

Unregistration reverses that sequence. All operators and the panel poll
through `context.has_skin_metadata()`, so the UI appears only when the active
object is an armature with the pose bone named
`Sedaia.Skin_Utility_Config`.

The panel lives in the 3D View sidebar under **Download Skins**. It edits the
username stored on that metadata bone, starts the router, opens player-data
storage, and exposes the rig's synchronization settings.

## Workflow

```text
Change Skin
    │
    ├── no local player JSON ──► Online Access check ──► SKIN_get
    │                                                     │
    │                                                     ├── Mojang profile + session API
    │                                                     ├── download skin and optional cape
    │                                                     ├── save JSON
    │                                                     └── SKIN_load(0)
    │
    └── local player JSON exists
          ├── refresh prompt enabled ──► Load / Add Entry / Clean Slate menu
          └── otherwise ──────────────► SKIN_load(-1)
```

- `SKIN_get` creates the first skin and cape entry for a player.
- `SKIN_add` fetches the current remote profile, compares its skin texture
  hash with the newest stored entry, and appends a new indexed entry only when
  the skin changed.
- `SKIN_load` selects an entry with Python list indexing. Index `-1` means the
  most recently stored skin. It assigns the downloaded image to the rig's
  configured image node, packs it into the blend, and can synchronize arm
  type and rig name.
- `SKIN_purge` either moves the player's directory into a sibling
  `playerdata_purge/` backup location or removes it after the menu confirmation,
  then retrieves fresh data.

Network actions require Blender's **Online Access** setting. The extension
manifest declares both network and file permissions, and `service.py` makes
timeout-bound requests through `core.network` using a 15-second timeout.

## Rig metadata contract

The skin feature deliberately stores configuration on the rig's
`Sedaia.Skin_Utility_Config` pose bone. A compatible rig needs these ID
properties:

| Property | Used by | Meaning |
| --- | --- | --- |
| `Username` | router, get, add, load, purge, panel | Minecraft player name and local storage key |
| `MatObj` | load | Substring used to find the child object holding the skin material |
| `SkinImageNodeID` | load | Material node name whose image is replaced and packed |
| `SyncArms` | load, panel | Enables arm model synchronization |
| `ArmPropBone` | load when `SyncArms` | Pose bone with the arm-type control |
| `ArmPropName` | load fallback | ID-property name for the arm-type control |
| `SyncName` | load, panel | Renames the armature object and data after loading |
| `RigName` | load when `SyncName` | Rig label appended to the player name |
| `SyncCape` | panel only | Optional control shown when provided by the rig |

`SKIN_load` first tries the arm bone's `ArmType` RNA property and falls back to
the configured ID property. The remote model value is `"1"` for Minecraft's
slim model and `"0"` otherwise. Cape metadata is downloaded and persisted, but
this module does not currently apply a cape texture.

## Local storage format

The default root is the extension's `playerdata` directory, configured in
`prefs.config["player_default_dir"]`. Each username has its own directory:

```text
playerdata/
└── <username>/
    ├── <username>_Data.json
    ├── <username>_Skin.png
    ├── <username>_Cape.png             # present only when the player has one
    ├── <username>_Skin_1.png
    └── <username>_Cape_1.png
```

The JSON document has top-level `UUID`, `NAME`, `SKINS`, and `CAPES` keys.
Skin entries carry `index`, `path`, `hash`, and `model`; cape entries carry
`index`, `path`, `hash`, and `exists`. `repository.save()` uses
`core.storage.write_json()`, which writes a temporary file and atomically
replaces the old JSON file.

## Change guide

- Add or rename Blender IDs in `constants.py`; keep the generated namespaces
  stable for existing rigs and UI calls.
- Keep Blender UI and operator code thin. Put remote parsing and downloading in
  `service.py`, and path or JSON changes in `repository.py`.
- Preserve the metadata-bone contract when changing rig assets. The module has
  no separate schema or migration layer.
- Test error paths for unavailable Online Access, invalid Mojang data, missing
  local files, and missing rig metadata. Blender runtime validation should also
  cover image packing, material-node lookup, and arm/name synchronization.

`features/skins_v2` is a separate, currently unregistered work-in-progress
module. It is not part of the workflow documented here.
