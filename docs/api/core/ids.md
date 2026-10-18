# `core.ids`

Stable identifiers for Blender classes and operators.

## `ID`

Build Blender IDs while keeping existing namespaces stable.

### `panel_for(self, rig: str) -> str`

Return the stable panel ID for a rig namespace.

### `operator_for(self, rig: str) -> str`

Return the stable operator ID for a rig namespace.

### `menu_for(self, rig: str) -> str`

Return the stable menu ID for a rig namespace.

### `list_for(self, rig: str) -> str`

Return the stable UI-list ID for a rig namespace.
