"""Configuration shared by the Skin Manager's type packages.

The Skin Manager names no rig. Each rig feature describes where its rig keeps
skin data with a `core.skin_targets.SkinTarget`, and the operators look up the
active rig's target in `core.skin_targets.registry`. Mojang endpoints live in
`core.mojang`.

Blender idnames live in each type package's own `constants.py`.
"""

# Feature namespace for idnames, e.g. `sedaia_rigs_skins.skin_router`.
# Changing it renames every Skin Manager idname and breaks keymaps and scripts.
NAMESPACE = "SKINS"
