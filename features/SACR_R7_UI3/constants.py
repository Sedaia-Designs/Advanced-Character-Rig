"""Names in the SACR R7.5.0 rig that this feature reads or writes.

Every name below was checked against ``lib/SACR.R7.5.0.blend``. Renaming one in
the rig breaks the code that uses it, so change both together.

`SKIN_TARGET` tells the Skin Manager where R7.5 keeps its skin data. The
feature adds it to `core.skin_targets.registry` in `__init__.py`, so the Skin
Manager never needs to know about this rig.

Blender idnames live in each type package's own `constants.py`.
"""

from enum import IntEnum, StrEnum

from ...core.databases.skins import SkinModel
from ...core.skin_targets import ArmTypeSync, BoneProp, SkinTarget, TextureSlot


class RigID(StrEnum):
    """Armature data property that identifies the rig, and R7.5's value for it."""

    PROPERTY = "rigID"
    SACR_R7_5 = "SACR.Rev_7.UI_3"


class RigBone(StrEnum):
    """Pose bones the rig UI and the Skin Manager read."""

    ROOT = "SACR_Root"
    RIG_PROPERTIES = "Rig_Properties"
    FACE_PROPERTIES = "Face_Properties"
    EYE_PROPERTIES = "Eye_Properties"
    EYEBROW_PROPERTIES = "Eyebrow_Properties"
    MOUTH_PROPERTIES = "Mouth_Properties"

    # Python helper bones: custom properties that point at rig data.
    PY_OBJECTS = "PythonConfig.Objects"
    PY_MATERIALS = "PythonConfig.Materials"
    PY_PANEL_HELPER = "PythonConfig.PanelHelper"
    PY_SKIN = "PythonConfig.Skin"


class SkinProp(StrEnum):
    """Custom properties on the `RigBone.PY_SKIN` bone."""

    USERNAME = "Username"  # str: the Java Edition username to fetch.
    SYNC_ARMS = "SyncArms"  # bool: set Arm Type from the skin model.
    SYNC_NAME = "SyncName"  # bool: rename the rig after the player.


class MaterialKey(StrEnum):
    """Keys on the `RigBone.PY_MATERIALS` bone that point at materials."""

    SKIN = "skin"


class SkinNode(StrEnum):
    """Node names in the skin material's node tree."""

    TEXTURE = "Skin_Texture"  # Image Texture node holding the skin image.


class RigProp(StrEnum):
    """Custom properties on the `RigBone.RIG_PROPERTIES` bone."""

    ARM_TYPE = "Arm Type"  # int, see `ArmType`.


class ArmType(IntEnum):
    """Values of ``Rig_Properties["Arm Type"]``. They are stored in rig files, so never change them."""

    DEFAULT = 0  # 4x4x12 px arms, Mojang's "classic" model.
    SLIM = 1  # 4x3x12 px arms, Mojang's "slim" model.
    SUPER_SLIM = 2  # 3x3x12 px arms. Custom, so a Mojang sync never sets it.


SKIN_TARGET = SkinTarget(
    label="SACR R7.5.0",
    rig_id_property=RigID.PROPERTY,
    rig_ids=frozenset({RigID.SACR_R7_5}),
    username=BoneProp(RigBone.PY_SKIN, SkinProp.USERNAME),
    skin=TextureSlot(BoneProp(RigBone.PY_MATERIALS, MaterialKey.SKIN), SkinNode.TEXTURE),
    arm_type=ArmTypeSync(
        toggle=BoneProp(RigBone.PY_SKIN, SkinProp.SYNC_ARMS),
        target=BoneProp(RigBone.RIG_PROPERTIES, RigProp.ARM_TYPE),
        values={SkinModel.CLASSIC: ArmType.DEFAULT, SkinModel.SLIM: ArmType.SLIM},
    ),
    sync_name=BoneProp(RigBone.PY_SKIN, SkinProp.SYNC_NAME),
)
