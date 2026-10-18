"""Stable identifiers for Blender classes and operators."""


class ID(str):
    """Build Blender IDs while keeping existing namespaces stable."""

    def panel_for(self, rig: str) -> str:
        return f"SEDAIA_RIGS_{rig}_PT_{self}"

    def operator_for(self, rig: str) -> str:
        return f"sedaia_rigs_{rig.lower()}_ot.{self}"

    def menu_for(self, rig: str) -> str:
        return f"SEDAIA_RIGS_{rig}_MT_{self}"

    def list_for(self, rig: str) -> str:
        return f"SEDAIA_RIGS_{rig}_UL_{self}"
