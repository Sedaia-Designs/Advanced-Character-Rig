"""Blender-free tests for `core.ids`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.ids import ID  # noqa: E402


class OperatorIDTests(unittest.TestCase):
    def test_uses_blender_python_form(self):
        self.assertEqual(ID("image_pack").operator_for("UTILS"), "sedaia_rigs_utils.image_pack")

    def test_module_does_not_repeat_type_marker(self):
        # Blender stores `module.name` as `MODULE_OT_name`; a module ending in
        # `_ot` would become `..._OT_OT_name`.
        module, _ = ID("skin_router").operator_for("SKINS").split(".")
        self.assertFalse(module.endswith("_ot"))

    def test_other_types_use_internal_form(self):
        self.assertEqual(ID("main").panel_for("skins"), "SEDAIA_RIGS_SKINS_PT_main")
        self.assertEqual(ID("existing").menu_for("skins"), "SEDAIA_RIGS_SKINS_MT_existing")
        self.assertEqual(ID("history").list_for("skins"), "SEDAIA_RIGS_SKINS_UL_history")


if __name__ == "__main__":
    unittest.main()
