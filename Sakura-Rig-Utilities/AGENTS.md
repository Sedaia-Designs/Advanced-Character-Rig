# Agent Guidelines

Use this file as the canonical guidance for AI agents working on Sedaia Rig
Interfaces. This repository contains a Python Blender Extension. It is not a
frontend application or an IntelliJ Platform plugin.

## Collaboration and Learning

The repository owner is learning Python, Blender's API, Blender Extensions,
and professional software engineering through this project. Pair as a senior
engineer who teaches while still moving requested work to a complete,
validated result.

- Use the `python-blender-mentoring` skill for implementation, refactoring,
  debugging, architecture, testing, code review, and Blender API explanations.
- Explain meaningful design decisions using the current code, relevant Blender
  lifecycle or Python concept, realistic alternatives, and the tradeoff behind
  the recommendation.
- Keep learning prompts focused and non-blocking when a safe, reversible
  assumption permits progress.
- Ask for the owner's hypothesis during reviews or debugging when practical,
  then distinguish observations, inferences, and conclusions.
- Offer a hint or scaffold before a full solution when the owner is actively
  implementing. Provide the full implementation when requested or when partial
  guidance would create unnecessary risk.
- Correct misconceptions directly and respectfully with a small example from
  this repository.
- If the owner asks to "just implement" or requests an urgent fix, prioritize
  concise execution while still explaining consequential design and safety
  decisions.
- Perform routine tests, formatting, Git operations, generated updates, and
  repetitive edits without turning them into lessons.
- Teaching does not grant permission for commits, pushes, releases,
  destructive operations, or other external side effects.

## Local Skills

Project-local skills live under `.agents/skills/`. Read and follow a skill when
the task matches its trigger:

- `python-blender-mentoring`: Python, Blender API, architecture, debugging,
  tests, reviews, and learning-oriented implementation.
- `blender-pycharm-workflow`: PyCharm project setup, Blender Development plugin
  configuration, Blender installation selection, API stubs, launch/debug,
  reload-on-save, extension source paths, or IDE-versus-runtime diagnosis.
- `edit-changelog`: changelog curation, `Unreleased`, release notes, or version
  section preparation. Do not edit `CHANGELOG.md` unless requested.
- `git-commit`: staging, commit-message preparation, or committing. Do not
  create a commit unless requested.

When multiple skills apply, use the smallest set that covers the task. Project
instructions in this file take precedence when they are more specific.

## Project Overview

Sedaia Rig Interfaces provides rig UI panels, rig and manifest download tools,
skin and image utilities, user preferences, and extension-local storage for
Sakura/Sedaia rig workflows.

Primary stack:

- Python 3
- Blender 5.0+ API
- Blender Extensions manifest system
- TOML metadata
- uv project metadata and lockfile
- Blender Development for PyCharm as optional IDE assistance

The PyCharm plugin assists development but is not a runtime dependency of this
extension.

## Repository Structure

- `extension/`: active Blender extension source.
- `extension/__init__.py`: top-level Blender registration entry point.
- `extension/blender_manifest.toml`: extension identity, compatibility,
  permissions, and build metadata.
- `extension/loader.py`: feature-package loading and registration order.
- `extension/preferences.py`: addon preferences and extension-local storage.
- `extension/interface/`: shared interface definitions.
- `extension/lib/`: extension-wide reusable Python logic.
- `extension/rig_manager/`: rig manager operators, panels, lists, and local
  reusable logic.
- `extension/skin_manager/`: skin manager feature package.
- `extension/wheels/`: declared extension wheels or placeholders.
- `tests/`: automated tests that can run outside Blender where practical.
- `.run/`: shared PyCharm run configurations.
- `.agents/skills/`: repository-local agent skills.
- `pyproject.toml`: Python project metadata and development dependencies.
- `uv.lock`: locked Python development environment.
- `.hidden/`: private or archived material; ignore unless explicitly requested.

Treat repository structure as observable state. Check current files before
assuming a package or module exists.

## Core Engineering Rules

- Keep changes scoped to the requested behavior and avoid unrelated refactors.
- Prefer Blender APIs and existing repository patterns over custom
  infrastructure.
- Keep functions focused. Extract reusable logic when it improves testability
  or removes meaningful duplication.
- Favor descriptive names over comments. Add comments only for non-obvious
  contracts, lifecycle constraints, or compatibility behavior.
- Preserve public behavior and stored data compatibility unless the requested
  change intentionally breaks them.
- Never treat type stubs as proof that code works inside Blender.

## Blender Extension Rules

- Keep active runtime code under `extension/`.
- Keep manifest metadata, permissions, build exclusions, platforms, and wheels
  in `extension/blender_manifest.toml`.
- Keep the manifest `id` stable unless an intentional migration is requested.
  It is the canonical extension identity used by Blender repositories.
- Declare `network` and `files` permissions accurately when a feature requires
  them.
- Check Blender's online-access state before performing network operations.
- Store downloaded rigs, manifests, presets, and user data beneath the
  configured addon data directory.
- Use `bpy.utils.extension_path_user(__package__, create=True)` for the default
  extension-local storage root.
- Keep production code independent of the Blender Development for PyCharm
  plugin and its bundled runtime.
- Report operator failures clearly with `self.report({"ERROR"}, message)` and
  return `{"CANCELLED"}` when the operation cannot complete.

## Network and File IO

- Keep reusable HTTP, JSON, path, and persistence logic in an appropriate
  `lib/` package rather than embedding it in a panel.
- Give network requests explicit timeouts.
- Validate HTTP status and response content before writing files or updating
  Blender state.
- Use context managers so responses and files close reliably.
- Write downloads to extension-local storage, create required parent
  directories, and avoid ambiguous paths such as an empty `Path()`.
- Prefer atomic replacement when a failed or interrupted download could corrupt
  an existing manifest or user file.
- Catch expected network, JSON, TOML, and filesystem failures at the boundary
  that can add useful context. Do not use broad exception handling to hide
  programming errors.
- Keep library functions independent of Blender UI where practical. Translate
  library failures into operator reports in the calling operator.
- Never print credentials, tokens, private asset URLs, or sensitive response
  data.

## Naming and Blender IDs

- Use the repository's `ID` helper for operator, panel, menu, and UI-list
  IDs when available.
- Operators use `Prefixer("name").operator`.
- Panels use `Prefixer("name").panel`.
- Menus use `Prefixer("name").menu`.
- UI lists use `Prefixer("name").list`.
- Add a missing ID helper to the inherited `ID` implementation before
  inventing a parallel naming system.
- Follow the existing filename convention for feature classes:
  `OT_*` or `OP_*` for operators, `PT_*` or `PANEL_*` for panels, and `UI_*`
  for UI lists. Match the convention of the owning package rather than
  renaming unrelated files.
- Imports must match filename casing exactly.

## Registration and Lifecycle

- Every feature package must expose `register()` and `unregister()`.
- Add new feature packages to `extension/loader.py` so they participate in the
  top-level lifecycle.
- Add feature modules to the owning package's module list.
- Register Blender classes with `bpy.utils.register_class`.
- Unregister modules and classes in reverse dependency order.
- Register properties only after their `PropertyGroup` classes and remove
  attached properties during unregistration.
- Keep registration idempotence and reload behavior in mind; stale classes,
  handlers, timers, or properties can survive a failed reload.
- Avoid executing registration as an import side effect outside an explicit
  development guard.

Use the established pattern:

```python
classes = (
    MyOperator,
)


def register():
    for cls in classes:
        U.register_class(cls)


def unregister():
    for cls in reversed(classes):
        U.unregister_class(cls)
```

## Python and Blender API Style

Prefer the existing aliases when the module uses the corresponding APIs:

```python
import bpy
import bpy.ops as O
import bpy.props as P
import bpy.types as T
import bpy.utils as U
```

- Use 4-space indentation.
- Follow the repository's current Python version and formatting conventions.
- Use type annotations for reusable non-RNA logic when they clarify contracts.
- Use double quotes for user-visible labels, descriptions, and reports.
- Match existing single-quoted internal enum identifiers and keys where
  consistency matters.
- Use forward slashes in documented paths.
- Keep operator `execute()` methods returning `{"FINISHED"}` or
  `{"CANCELLED"}`.
- Avoid noisy debug output. Prefer operator reports and guard developer-only
  diagnostics or UI behind `prefs.dev_mode`.
- Do not introduce mutable module-level state when Blender-owned properties or
  a clearly owned service object are more appropriate.

## Properties and State

- Do not register custom `bpy.props` directly on `bpy.types.PoseBone`.
- Store bone-specific data as ID properties such as
  `bone["property_name"] = value`.
- Store extension-level UI state in registered `PropertyGroup` classes attached
  to stable Blender types or in addon preferences.
- Use the repository's preferences accessor instead of duplicating addon lookup
  logic.
- Keep persisted property names and enum identifiers stable unless migration
  behavior is included.
- Ensure dynamically attached Blender properties are removed during
  unregistration.

## Operators and UI

- Keep panels and operators thin. Move reusable business, network, and file
  logic into a local `lib/` package.
- Add `poll()` when a panel or operator requires a particular active object,
  mode, rig ID, selection, or Blender context.
- Never assume `context.active_object`, its data, or a selected list item is
  present without checking.
- Use established 3D View sidebar categories, especially SACR-related
  categories already used by the owning feature.
- Prefer Blender-native layout primitives such as `row(align=True)`,
  `column()`, `box()`, `template_list`, standard icons, and concise labels.
- Keep destructive actions explicit and provide confirmation where data loss
  would be surprising.
- Ensure important workflows remain understandable without relying only on an
  icon or color.

## Blender Development for PyCharm

Use `blender-pycharm-workflow` for IDE-specific tasks.

- Configure `extension/` as the source folder.
- Treat `extension/blender_manifest.toml` as the canonical extension identity
  and compatibility source.
- Use the project uv interpreter and version-matched `bpy` stubs for completion
  and static inspection.
- Prefer the shared `Launch Blender` configuration for interactive validation.
- Restart Blender after manifest identity, permissions, package structure, or
  stubborn registration changes when reload-on-save is insufficient.
- Separate configuration failures, import/registration failures, and loaded
  extension behavior failures before changing code.
- If evidence indicates a companion-plugin defect, inspect
  `/Users/Sakura/Documents/IdeaProjects/blender_pycharm` only when the user asks
  to diagnose or change it. Read that repository's `AGENTS.md` first and keep
  changes in the two repositories separate.

## Testing and Verification

Validation must be proportional to risk.

- For Python edits, run `python -m compileall extension`.
- Run targeted tests under `tests/` for reusable logic and regression coverage.
- Add tests for new logic and important edge cases when it can be isolated from
  Blender.
- For manifest edits, parse or inspect
  `extension/blender_manifest.toml` and confirm identity, compatibility,
  permissions, build exclusions, and wheels are accurate.
- For registration, RNA properties, context-sensitive operators, UI drawing,
  reload behavior, and Blender data access, validate inside Blender when
  practical.
- Test scripts and commands before documenting or recommending them.
- State what was run, what passed, and what was not validated. Distinguish
  stub-backed checks from actual Blender runtime checks.
- There is no frontend build step for this repository.

## Dependencies and Build Hygiene

- Keep `pyproject.toml` and `uv.lock` aligned when dependencies change.
- Do not edit generated artifacts unnecessarily.
- Do not commit Python caches, local Blender state, virtual environments,
  packaged ZIPs, wheels, test caches, or downloaded private assets.
- Keep `.gitignore` aligned with generated Python, Blender, IDE, and local
  asset files.
- Verify ignored generated files are not tracked before committing.

## Documentation

- Read `README.md`, `GUIDELINES.md`, this file, and the owning feature before
  broad changes.
- Treat current code, tests, manifest metadata, README, and changelog as the
  evidence for documented behavior.
- Keep public documentation task-focused and exclude local-machine paths,
  credentials, private assets, and security-sensitive implementation details.
- Use repository-relative paths when documenting source locations.
- Do not modify `.hidden/` unless the user explicitly requests it.
- Do not edit `CHANGELOG.md` unless requested; use `edit-changelog` when it is
  in scope.
- Do not create or update `.logs/` unless asked for session logging or a context
  summary. Use `.logs/summary_YYYY-MM-DD.md` for a requested summary.

## Planning

For work that benefits from a written plan:

- Begin with a short scope statement defining what will change and what is out
  of scope.
- Use small, ordered, testable steps with clear completion criteria.
- Resolve important risks and unknowns before dependent integration work.
- Include explicit validation and documentation steps when applicable.
- Track progress as work proceeds.
- Include a commit step only when the user explicitly requested a commit.

## Git and Repository Safety

- Inspect `git status --short --branch` before broad edits.
- Treat staged, unstaged, and untracked changes as user-owned work.
- Preserve unrelated work and never discard it without explicit permission.
- Treat a deletion plus equivalent addition as a possible move during review.
- Do not create a commit unless explicitly requested. Use `git-commit` when
  committing.
- Use author `SakuraSedaia <sakusedaia@outlook.com>` unless the user specifies
  another author.
- Do not add Junie or another co-author unless explicitly requested.
- Use `type[Module_name]: Description`, or `type: Description` when more than two
  modules are affected.
- Valid types include `Feature`, `Refactor`, `Chore`, `Cleanup`, `Asset`, `Fix`,
  `Docs`, `Style`, and `Test`.
- Keep the complete subject at or below 150 characters.
- Never push, force-push, tag, publish, release, or otherwise affect a remote
  without explicit permission.
