"""Blender-free tests for `core.skin_targets`.

Run from the repository root with: uv run python -m unittest discover -s tests
"""

import sys
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.databases.skins import SkinModel  # noqa: E402
from core.skin_targets import (  # noqa: E402
    ArmTypeSync,
    BoneProp,
    SkinTarget,
    SkinTargetRegistry,
    TextureSlot,
)


def armature(**props):
    """Return a stand-in armature object whose data supports item access."""
    return SimpleNamespace(type="ARMATURE", data=props or {"_": None})


ARMS = ArmTypeSync(
    toggle=BoneProp("Config", "SyncArms"),
    target=BoneProp("Props", "Arm Type"),
    values={SkinModel.CLASSIC: 0, SkinModel.SLIM: 1},
)
TARGET = SkinTarget(
    label="Test Rig",
    rig_id_property="rigID",
    rig_ids=frozenset({"TEST.1"}),
    username=BoneProp("Config", "Username"),
    skin=TextureSlot(BoneProp("Materials", "skin"), "Skin_Texture"),
    arm_type=ARMS,
)


class ArmTypeSyncTests(unittest.TestCase):
    def test_value_for_each_model(self):
        self.assertEqual(ARMS.value_for(SkinModel.CLASSIC), 0)
        self.assertEqual(ARMS.value_for(SkinModel.SLIM), 1)
        self.assertEqual(ARMS.value_for("slim"), 1)

    def test_rejects_missing_model(self):
        with self.assertRaisesRegex(ValueError, "slim"):
            ArmTypeSync(ARMS.toggle, ARMS.target, {SkinModel.CLASSIC: 0})

    def test_values_cannot_change_after_creation(self):
        source = {SkinModel.CLASSIC: 0, SkinModel.SLIM: 1}
        sync = ArmTypeSync(ARMS.toggle, ARMS.target, source)
        source[SkinModel.SLIM] = 5
        self.assertEqual(sync.value_for(SkinModel.SLIM), 1)
        with self.assertRaises(TypeError):
            sync.values[SkinModel.SLIM] = 5  # type: ignore[index]


class SkinTargetTests(unittest.TestCase):
    def test_matches_rig_id(self):
        self.assertTrue(TARGET.matches(armature(rigID="TEST.1")))
        self.assertFalse(TARGET.matches(armature(rigID="OTHER")))
        self.assertFalse(TARGET.matches(None))

    def test_optional_features_default_to_none(self):
        bare = SkinTarget("Bare", "rigID", frozenset({"B"}), TARGET.username, TARGET.skin)
        self.assertIsNone(bare.arm_type)
        self.assertIsNone(bare.sync_name)

    def test_rejects_empty_rig_ids(self):
        with self.assertRaises(ValueError):
            replace(TARGET, rig_ids=frozenset())

    def test_rejects_empty_label(self):
        with self.assertRaises(ValueError):
            replace(TARGET, label="")


class SkinTargetRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = SkinTargetRegistry()

    def test_for_rig_finds_registered_target(self):
        self.registry.register(TARGET)
        self.assertIs(self.registry.for_rig(armature(rigID="TEST.1")), TARGET)
        self.assertIsNone(self.registry.for_rig(armature(rigID="OTHER")))

    def test_registering_equal_target_twice_is_a_no_op(self):
        self.registry.register(TARGET)
        self.registry.register(replace(TARGET))
        self.assertEqual(len(self.registry), 1)

    def test_rejects_a_second_target_for_the_same_rig_id(self):
        self.registry.register(TARGET)
        with self.assertRaisesRegex(ValueError, "Test Rig"):
            self.registry.register(replace(TARGET, label="Impostor"))

    def test_same_rig_id_under_another_property_is_allowed(self):
        self.registry.register(TARGET)
        self.registry.register(replace(TARGET, label="Other", rig_id_property="sacr_id"))
        self.assertEqual(len(self.registry), 2)

    def test_unregister_by_value_after_reload(self):
        self.registry.register(TARGET)
        self.registry.unregister(replace(TARGET))  # An equal object, as after a reload.
        self.assertEqual(len(self.registry), 0)

    def test_clear(self):
        self.registry.register(TARGET)
        self.registry.clear()
        self.assertEqual(list(self.registry), [])


if __name__ == "__main__":
    unittest.main()
