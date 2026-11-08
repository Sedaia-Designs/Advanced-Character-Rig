"""Local UI helpers for the SACR R7.5 rig panels."""

from . import ui

RIG_ID_GROUP = "SACR7_UI3"


class ID(str):
    """Build Blender IDs while keeping existing namespaces stable."""

    def panel_for(self, rig: str) -> str:
        """Return the stable panel ID for a rig namespace."""
        return f"SEDAIA_RIGS_{rig}_PT_{self}"

    def operator_for(self, rig: str) -> str:
        """Return the stable operator ID for a rig namespace."""
        return f"sedaia_rigs_{rig.lower()}_ot.{self}"
