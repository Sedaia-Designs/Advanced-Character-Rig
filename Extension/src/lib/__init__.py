"""
The Libs package is where all the utility functions and classes are stored. These functions do not directly use bpy, however, are relied on by the different operators. These can range anywhere from simple downloaders, to even image processing.
"""

from . import exceptions


class ID(str):
    @property
    def panel(self):
        return f"SEDAIA_RIGS_PT_{self}"

    @property
    def operator(self):
        return f"sedaia_rigs_ot.{self}"

    @property
    def menu(self):
        return f"SEDAIA_RIGS_MT_{self}"

    @property
    def list(self):
        return f"SEDAIA_RIGS_UL_{self}"
