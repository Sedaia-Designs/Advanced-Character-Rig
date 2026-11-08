"""Stable identifiers for Blender classes and operators.

Pattern: Factory. `ID` is the one place that builds idnames, so every package
gets the same `ID_PREFIX` and type-marker layout.
"""

# Shared prefix for every Blender ID the project registers. Changing it renames
# every operator, panel, menu, and UI list, which breaks user keymaps and scripts.
ID_PREFIX = "sedaia_rigs"


class ID(str):
    """Factory for Blender IDs that keeps existing namespaces stable."""

    def panel_for(self, rig: str) -> str:
        """Return the stable panel ID for a rig namespace."""
        return f"{ID_PREFIX.upper()}_{rig.upper()}_PT_{self}"

    def operator_for(self, rig: str) -> str:
        """Return the stable operator ID for a rig namespace."""
        return f"{ID_PREFIX.lower()}_{rig.lower()}_ot.{self}"

    def menu_for(self, rig: str) -> str:
        """Return the stable menu ID for a rig namespace."""
        return f"{ID_PREFIX.upper()}_{rig.upper()}_MT_{self}"

    def list_for(self, rig: str) -> str:
        """Return the stable UI-list ID for a rig namespace."""
        return f"{ID_PREFIX.upper()}_{rig.upper()}_UL_{self}"
