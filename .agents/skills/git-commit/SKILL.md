---
name: git-commit
description: Create safe, logically grouped Git commits using this repository's bracketed type-and-module subject format. Use when the user asks to commit changes, create a Git commit, prepare a commit message, stage a logical change for commit, or invokes `/commit`. Analyze staged and unstaged diffs, select only the intended files, generate a project-compliant message, and execute the commit without altering unrelated work.
---

# Git Commit

Create focused commits from the actual repository diff. Follow `AGENTS.md` when it is more specific than this skill.

## Format the Subject

Use one of these forms:

```text
[Type -> module] Description
[Type] Description
```

- Choose a project-approved type such as `Feature`, `Refactor`, `Chore`, `Cleanup`, `Asset`, `Fix`, `Docs`, `Style`, or `Test`.
- Add `-> module` when one or two feature areas are affected. Derive a short lowercase module from `extension/`, such as `rig-manager`, `skin-manager`, `preferences`, or `manifest`.
- Omit the module when more than two feature areas are affected.
- Write an imperative, sentence-case description without a trailing period.
- Keep the complete subject at or below 150 characters.

Do not use Conventional Commits syntax such as `feat(scope): description`.

## Inspect the Repository

1. Read the applicable `AGENTS.md`.
2. Inspect recent subjects with `git log -20 --pretty=format:'%s'`.
3. Inspect `git status --short --branch`, `git diff --staged`, and `git diff`.
4. Treat all existing changes as user work. Identify the exact files forming the requested logical change.
5. Do not restore, reset, overwrite, or silently absorb unrelated work.

This repository may contain a broad in-progress migration from `src/` to `extension/`. Do not assume all migration changes belong in one commit. Group them by coherent behavior unless the user explicitly requests one migration commit.

## Stage and Verify

Stage explicit paths only:

```bash
git add path/to/file1 path/to/file2
```

- Keep one logical change per commit.
- Avoid `git add .` when unrelated changes exist.
- Never commit secrets, credentials, local Blender state, virtual environments, packaged archives, caches, downloaded private assets, or `.hidden/`.
- If unrelated files are already staged, preserve their staged state. Ask for direction when isolation would require changing user-owned staging.

Review the exact candidate:

```bash
git diff --staged --stat
git diff --staged
git diff --staged --check
```

Run validation proportional to the staged change. For Python, prefer `python -m compileall extension`; run relevant tests when available. Inspect `extension/blender_manifest.toml` after manifest changes.

## Commit and Confirm

Commit using the required author unless the user specifies another:

```bash
git commit --author="SakuraSedaia <sakusedaia@outlook.com>" -m "[Type -> module] Description"
```

Do not add Junie or another co-author unless the user explicitly requests it.

Confirm with:

```bash
git show --stat --oneline HEAD
git status --short --branch
```

Report the hash, subject, included change, validation, and remaining uncommitted work.

## Preserve Git Safety

- Never change Git configuration.
- Never discard changes unless the user explicitly requests the exact action.
- Never bypass hooks with `--no-verify` unless explicitly requested.
- If a hook fails, fix an in-scope problem and retry; do not amend unless explicitly requested.
- Never push, force-push, tag, publish, or otherwise affect a remote without explicit permission.
