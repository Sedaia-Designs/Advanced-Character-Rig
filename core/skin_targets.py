"""Rig descriptions that tell the Skin Manager where a rig keeps its skin data.

The Skin Manager is not tied to one rig. Each rig feature describes its rig
with a `SkinTarget` and adds it to `registry` when the feature registers. The
Skin Manager finds the active rig's target with `registry.for_rig(obj)` and
reads and writes only the bones, keys, and nodes that target names.

Optional parts are the rig's feature flags. A rig without an Arm Type
property leaves `arm_type` as `None`, and the Skin Manager skips arm syncing;
likewise for `sync_name`.

Every name here is plain data, so this module needs no Blender and a rig's
target can be checked in plain Python tests.

Pattern: Singleton. `registry` is the one process-wide `SkinTargetRegistry`,
because rig features and the Skin Manager register separately and never import
each other. Tests build their own `SkinTargetRegistry` instead of touching it.
"""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .databases.skins import SkinModel
from .rigs import matches_rig_id


@dataclass(frozen=True, slots=True)
class BoneProp:
    """A custom property on a pose bone, read as ``rig.pose.bones[bone][key]``."""

    bone: str
    key: str


@dataclass(frozen=True, slots=True)
class TextureSlot:
    """The Image Texture node a downloaded texture is applied to.

    `material` is the bone property that points at the material, and `node` is
    the name of the image node in that material's node tree.
    """

    material: BoneProp
    node: str


@dataclass(frozen=True, slots=True)
class ArmTypeSync:
    """How a rig sets its arm width from a skin's model.

    `toggle` is the bool property that turns syncing on, `target` is the int
    property that receives the value, and `values` maps every `SkinModel` to
    the rig's value for it.
    """

    toggle: BoneProp
    target: BoneProp
    values: Mapping[SkinModel, int]

    def __post_init__(self):
        missing = set(SkinModel) - set(self.values)
        if missing:
            names = ", ".join(sorted(model.value for model in missing))
            raise ValueError(f"ArmTypeSync.values has no value for: {names}")
        # Copy into a read-only view so a frozen target cannot change later.
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))

    def value_for(self, model: SkinModel) -> int:
        """Return the rig's Arm Type value for a skin `model`."""
        return self.values[SkinModel(model)]


@dataclass(frozen=True, slots=True)
class SkinTarget:
    """Where one rig keeps everything the Skin Manager reads and writes.

    `label` names the rig in reports. A rig matches when its armature data
    property `rig_id_property` holds one of `rig_ids`.
    """

    label: str
    rig_id_property: str
    rig_ids: frozenset[str]
    username: BoneProp
    skin: TextureSlot
    arm_type: ArmTypeSync | None = None  # None: the rig has no arm-type sync.
    sync_name: BoneProp | None = None  # None: the rig has no rename-after-player toggle.

    def __post_init__(self):
        if not self.label:
            raise ValueError("label must be a non-empty string")
        rig_ids = frozenset(self.rig_ids)
        if not rig_ids:
            raise ValueError("rig_ids must name at least one rig ID")
        object.__setattr__(self, "rig_ids", rig_ids)

    def matches(self, obj) -> bool:
        """Return whether Blender object `obj` is a rig this target describes."""
        return matches_rig_id(obj, self.rig_id_property, self.rig_ids)


class SkinTargetRegistry:
    """The rigs the Skin Manager can work on, in registration order."""

    def __init__(self):
        self._targets: list[SkinTarget] = []

    def register(self, target: SkinTarget) -> None:
        """Add `target`. Registering an equal target again does nothing.

        Raises `ValueError` if a different target already claims one of its
        rig IDs, since the Skin Manager could not tell which one applies.
        """
        if target in self._targets:
            return
        for existing in self._targets:
            shared = target.rig_ids & existing.rig_ids
            if existing.rig_id_property == target.rig_id_property and shared:
                raise ValueError(
                    f"Rig ID {sorted(shared)[0]!r} is already registered by {existing.label!r}"
                )
        self._targets.append(target)

    def unregister(self, target: SkinTarget) -> None:
        """Remove `target` if it is registered.

        Targets are compared by value, so an add-on reload that rebuilds an
        equal target still removes the old one.
        """
        self._targets = [existing for existing in self._targets if existing != target]

    def for_rig(self, obj) -> SkinTarget | None:
        """Return the target that describes Blender object `obj`, or `None`."""
        return next((target for target in self._targets if target.matches(obj)), None)

    def clear(self) -> None:
        """Remove every target."""
        self._targets.clear()

    def __iter__(self) -> Iterator[SkinTarget]:
        return iter(tuple(self._targets))

    def __len__(self) -> int:
        return len(self._targets)


# The process-wide registry that rig features add their targets to.
registry = SkinTargetRegistry()
