# Rig Interface Guardrail System

To allow multiple versions of the Sakura Character Rig (SACR) to run concurrently without property pollution or UI collisions, the following guardrail system MUST be followed.

## 1. Property Management

### No PoseBone Pollution
NEVER register `bpy.props` directly on `bpy.types.PoseBone`. This pollutes every bone in every armature in the Blender session.

### Instance-Level Storage
Store all bone-specific data as **ID Properties** (Instance-Level).
```python
bone["MyProperty"] = value
```

### Proxy PropertyGroups
Use a version-specific `PropertyGroup` registered on `bpy.types.Scene` to provide the UI with access to these ID properties.
- **Naming Convention**: `sacr_XX_rig_props` where `XX` is the version (e.g., `sacr_73_rig_props`).
- **Path**: `context.scene.sacr_73_rig_props.UI_Property`

### PropInterface
Use a `PropInterface` class to handle the redirection between the UI proxy property and the bone's ID property. It MUST validate the `rigID` before allowing access.

```python
def get_bone(self):
    obj = bpy.context.active_object
    if obj and obj.type == 'ARMATURE' and obj.pose:
        if obj.data.get("rigID") == self.ui_version:
            return obj.pose.bones.get(self.bone_name)
    return None
```

## 2. UI Guardrails

### Panel Polling
Individual panels SHOULD NOT implement their own `poll()` method. Instead, they MUST inherit from a version-specific base class or a common base class (like `SACR7_PT_Common`) that handles the `poll()` logic automatically.

This is managed by setting a `ui_version` class attribute on the panel class, which the base class uses to validate the `rigID`.

```python
class SACR7_UI3_PT_Settings(SACR7_PT_Common):
    ui_version = 3  # Base class poll() uses this to check for UI_3 rigs
    bl_label = "Settings"
    # ...
```

### Concurrent Registration
All versions of the addon should be registered simultaneously. The `toolwindow/__init__.py` acts as the master registry, calling `register()` on each versioned sub-module. Each versioned module is responsible for its own versioned `PropertyGroup` and Panels.
