"""
The Lib's package is a central store for commonly used code artifacts, including but not limited to Types declarations, Image Data manipulations, Exception declarations, etc.
"""

from . import exceptions
from . import types
from . import file


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
