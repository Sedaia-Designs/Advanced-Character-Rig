"""Blender-free tests for the shared core helpers.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.images import is_packed  # noqa: E402
from core.lookup import lookup_name  # noqa: E402
from core.rigs import matches_rig_id  # noqa: E402


def armature(**props):
    """Return a stand-in armature object whose data supports item access."""
    return SimpleNamespace(type="ARMATURE", data=props or {"_": None})


class IsPackedTests(unittest.TestCase):
    def test_packed_image(self):
        self.assertTrue(is_packed(SimpleNamespace(packed_files=["data"])))

    def test_unpacked_image(self):
        self.assertFalse(is_packed(SimpleNamespace(packed_files=[])))

    def test_missing_image(self):
        self.assertFalse(is_packed(None))


class LookupNameTests(unittest.TestCase):
    items = [SimpleNamespace(name="Body"), SimpleNamespace(name="MaterialEditor.001")]

    def test_returns_first_partial_match(self):
        self.assertIs(lookup_name(self.items, "MaterialEditor"), self.items[1])

    def test_returns_none_without_match(self):
        self.assertIsNone(lookup_name(self.items, "Armor"))


class MatchesRigIdTests(unittest.TestCase):
    def test_matching_id(self):
        self.assertTrue(matches_rig_id(armature(rigID="SACR.Rev_7.UI_3"), "rigID", ("SACR.Rev_7.UI_3",)))

    def test_any_of_several_ids(self):
        self.assertTrue(matches_rig_id(armature(sacr_id="sacr_1"), "sacr_id", ["SACR.Rev_7", "sacr_1"]))

    def test_other_id(self):
        self.assertFalse(matches_rig_id(armature(sacr_id="other"), "sacr_id", ["SACR.Rev_7", "sacr_1"]))

    def test_missing_property(self):
        self.assertFalse(matches_rig_id(armature(), "rigID", ("SACR.Rev_7.UI_3",)))

    def test_not_an_armature(self):
        mesh = SimpleNamespace(type="MESH", data={"rigID": "SACR.Rev_7.UI_3"})
        self.assertFalse(matches_rig_id(mesh, "rigID", ("SACR.Rev_7.UI_3",)))

    def test_no_active_object(self):
        self.assertFalse(matches_rig_id(None, "rigID", ("SACR.Rev_7.UI_3",)))


if __name__ == "__main__":
    unittest.main()
