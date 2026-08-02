# Sedaia Rig Interface - Unified Coding Standards & Guidelines

This document outlines the architectural patterns, coding standards, and development workflows for the Sedaia Rig Interface project, ensuring consistency and compatibility across all modules.

## 1. Project Architecture & Patterns

### 1.1 Prefixer System
Standardize naming for operators, panels, and menus using the `ID` class in `src/preferences.py` to prevent UI collisions.
- **Operator ID**: `sedaia_rigs_ot.your_op_name`
- **Panel ID**: `SEDAIA_RIGS_PT_your_panel_name`
- **Menu ID**: `SEDAIA_RIGS_MT_your_menu_name`

### 1.2 Modular Registration
- Each submodule (e.g., `skin_manager`, `rig_manager`) must have its own `register()` and `unregister()` functions.
- The main `src/__init__.py` acts as the master registry, calling these functions in order.
- When a module contains more than one class, use the following snippet for registration:
```python
classes = [
  <classes>
]

def register():
    for cls in classes:
        U.register_class(cls)

def unregister():
    for cls in classes:
        U.unregister_class(cls)
```

### 1.3 Library Centralization
- **Shared Logic**: Common Blender or filesystem operations (e.g., file existence, network checks) belong in `src/lib/`.
- **Module Logic**: Complex module-specific logic (e.g., skin application, rig downloading) must be in a `lib/` subfolder within that module.
- **Thin Operators**: Operators should be thin wrappers that call library functions.

### 1.4 Extension Structure & Manifest
- **Root Directory**: Active addon code is in `src/`.
- **Manifest**: Every extension must include `src/blender_manifest.toml` with required metadata (`id`, `version`, `name`, `maintainer`, `license`, `permissions`).
- **Permissions**: Explicitly state required permissions (e.g., `network`, `files`) with brief explanations.

---

## 2. Python Style & API Usage

### 2.1 Blender API Aliasing
Always use these standard aliases for consistency:
```python
import bpy
import bpy.types as T
import bpy.props as P
import bpy.ops as O
import bpy.utils as U
```
Use direct module calls (e.g., `U.register_class()` instead of `bpy.utils.register_class()`).

### 2.2 Naming & Formatting
- **Classes**: `CamelCase` (e.g., `MyOperator`).
- **Variables/Modules**: `snake_case` (e.g., `my_module`).
- **Indentation**: 4 spaces (never tabs).
- **Line Length**: Max 79 characters (PEP8).
- **Quotes**:
  - Single quotes (`'`) for internal identifiers, enums, and keys.
  - Double quotes (`"`) for user-facing strings and UI labels.

---

## 3. Property & UI Management

### 3.1 Property Storage
- **No PoseBone Pollution**: NEVER register `bpy.props` on `bpy.types.PoseBone`.
- **Instance-Level Data**: Store bone-specific data as **ID Properties** (`bone["MyProperty"] = value`).
- **Global State**: Use `PropertyGroup` registered on `bpy.types.Scene` for addon-level state (e.g., skin/rig lists).

### 3.2 UI Guardrails
- **Panel Polling**: Panels must implement a `poll()` method to appear only when relevant (e.g., when a supported armature is active). This guideline can be omitted for global panels.
  ```python
  @classmethod
  def poll(cls, context):
      obj = context.active_object
      return obj and obj.type == 'ARMATURE' and obj.data.get("rigID") == "EXPECTED_ID"
  ```
- **UI Categorization**: Use `bl_category = "SACR"` or specific sub-categories like `"SACR Skins"` in the 3D View sidebar.
- **Clean Layout**: Use `layout.box()`, `layout.row(align=True)`, and `layout.column()`. Prefer icons for feedback.

---

## 4. Best Practices & Workflow

### 4.1 Error Handling & Local Storage
- **Error Handling**: Use `try-except` for network/IO. Report errors via `self.report({'ERROR'}, message)` in operators.
- **Local Storage**: Use `U.extension_path_user(__package__, create=True, path="")` for local addon files (Blender Extension guidelines).

### 4.2 Versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking changes (UI reworks, API changes).
- **MINOR**: Backward-compatible new functionality.
- **PATCH**: Bug fixes and internal improvements.

### 4.3 Development Workflow
- **No Redundancy**: Use utility modules for shared logic; avoid duplicate classes.
- **Cleanup**: Remove unused variables, redundant parentheses, and debug prints (use `self.report()`).
- **Commits**: Group 1-2 features per commit using logical prefixes (e.g., `feat[module]`, `fix[module]`, `refactor[module]`, `chore`, `docs`).
  - **Commit Authorship**: Always author commits as `SakuraSedaia <sakusedaia@outlook.com>`.
  - **Co-Authorship**: Always include the `Co-authored-by: Junie <junie@jetbrains.com>` trailer in all commits.
- **Changelog Style**: All `CHANGELOG.md` entries must follow a standardized hierarchical structure:
  - **Level 1 Header (#)**: Version number (e.g., `# Version 4.0.0`).
  - **Level 2 Header (##) - Summary**: A brief overview of the release's purpose and major shifts.
  - **Level 2 Header (##) - Categories**: Descriptive sections grouping changes (e.g., `## General Extension Changes`, `## Rig UI Changes`).
  - **Level 3 Header (###) - Specifics**: Modules, features, or systems affected within a category (e.g., `### Prefixer System`).
  - **Bullet Points**: Use concise bullet points for individual changes.
  - **Separators**: Use a horizontal rule (`---`) between major version entries.
- **Archives**: Do not modify files in `archives/` or reference them unless explicitly requested.

### 4.4 AI Prompt Aliases
- **No Edit:**: When this prefix is used, no code changes shall be made.
- **Perform Systematic Commits**: When this alias is called, perform systematic commits containing 1-2 features per commit, using proper prefixing as defined in Section 4.3 (e.g., `feat[module]`, `fix[module]`, `refactor[module]`, `chore`, `docs`). Include the required co-author trailer in all commits.
