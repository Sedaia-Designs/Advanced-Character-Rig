"""Shared naming for Blender classes in the extension."""


class ID(str):
    """Build Blender IDs while keeping each feature's existing namespace."""

    @property
    def panel(self):
        return self.panel_for("GLOBAL")

    @property
    def operator(self):
        return self.operator_for("GLOBAL")

    @property
    def menu(self):
        return self.menu_for("GLOBAL")

    @property
    def list(self):
        return self.list_for("GLOBAL")

    def panel_for(self, rig):
        return f"SEDAIA_RIGS_{rig}_PT_{self}"

    def operator_for(self, rig):
        return f"sedaia_rigs_{rig.lower()}_ot.{self}"

    def menu_for(self, rig):
        return f"SEDAIA_RIGS_{rig}_MT_{self}"

    def list_for(self, rig):
        return f"SEDAIA_RIGS_{rig}_UL_{self}"
