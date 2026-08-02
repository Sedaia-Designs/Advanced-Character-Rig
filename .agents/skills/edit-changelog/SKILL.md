---
name: edit-changelog
description: Edit, curate, or review this Blender src's CHANGELOG.md and release notes using Keep a Changelog conventions. Use when Codex needs to update Unreleased, prepare a version section, derive notable changes since the latest release, split overloaded bullets, remove commit-history noise, or verify that entries describe only the final user-visible release delta.
---

# Edit Changelog

Produce a human-readable account of notable net changes between the previous released extension and the current state. Treat commits as evidence, not as changelog entries. Do not edit `CHANGELOG.md` unless the user asks.

## Establish the Release Baseline

1. Read `CHANGELOG.md`, `extension/blender_manifest.toml`, `pyproject.toml`, and repository release conventions.
2. Identify the target release and predecessor from explicit metadata, changelog headings, and matching tags.
3. Inspect the full predecessor-to-`HEAD` range plus relevant staged and unstaged work when updating `Unreleased`.
4. Compare final behavior with the predecessor. Record only the resulting delta.
5. Reconcile version, release channel, compatibility, and date claims with the manifest; do not silently change manifest metadata.

Do not log intermediate defects that were fixed, reverted, replaced, or removed before release.

## Curate Notable Outcomes

- Write for extension users and contributors rather than mirroring commits or file diffs.
- Include notable final features, changes, removals, deprecations, security changes, compatibility changes, and fixes.
- Omit implementation churn, file moves, formatting, merge activity, test-only maintenance, and transient defects unless they materially affect the final release.
- Describe observable Blender behavior. Mention internal classes, files, registration plumbing, or storage layout only when users or contributors need it.
- Do not invent motivation, impact, compatibility, or Blender-version claims unsupported by code, tests, docs, or metadata.

Keep one independently meaningful outcome per bullet. Keep tightly coupled cause-and-result wording together, but split unrelated behavior joined only by implementation or module.

## Apply Keep a Changelog

Maintain reverse chronological order and an `Unreleased` section at the top. Use ISO dates (`YYYY-MM-DD`) for releases.

Use standard headings:

- `Added`
- `Changed`
- `Deprecated`
- `Removed`
- `Fixed`
- `Security`

Preserve established formatting unless it conflicts with repository instructions. Omit empty headings unless the file establishes another convention. When cutting a release, move curated entries into a linkable version heading, retain `Unreleased`, and update comparison links when present.

## Verify the Edit

1. Confirm every bullet is true relative to the predecessor.
2. Confirm temporary same-cycle defects and reverted work are absent.
3. Separate unrelated outcomes and merge duplicates.
4. Confirm category, order, date, version, links, wrapping, punctuation, and inline code.
5. Confirm Blender compatibility and extension names match the manifest and README.
6. Review the changelog diff separately from implementation changes.
