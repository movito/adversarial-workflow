# ADV-0048: Fix find_task_file Boundary Matching

**Status**: Done
**Priority**: High
**Type**: Bug Fix
**Estimated Effort**: 10 minutes
**Created**: 2026-03-07
**Updated**: 2026-03-11 (simplified — no full script replacement needed)
**Parent**: ADV-0039

## Summary

Fix the `find_task_file` function in `scripts/core/project` to use
boundary-aware matching. The current implementation uses substring matching
(`in`), which causes `ADV-1` to match `ADV-10`, `ADV-11`, etc.

**Scope change**: The original spec called for replacing the entire upstream
`project` script and patching back our fix. After analysis, the diff between
our version and upstream is only 91 lines — almost entirely Ruff formatting
differences and path references (`./scripts/core/project` vs `./project`).
Our version already has all upstream features (setup, install-evaluators, uv
detection). Only the `find_task_file` fix is needed.

## Current (Buggy)

```python
def find_task_file(task_id: str, project_dir: Path) -> Path | None:
    """Find a task file by ID across all workflow folders."""
    tasks_dir = project_dir / "delegation" / "tasks"
    task_id_upper = task_id.upper()
    for folder in tasks_dir.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.md"):
            if task_id_upper in file.name.upper():
                return file
    return None
```

## Fixed (Boundary-Aware)

```python
def find_task_file(task_id: str, project_dir: Path) -> Path | None:
    """Find a task file by ID across all workflow folders.
    Uses boundary-aware matching to prevent ADV-1 from matching ADV-10, etc.
    """
    tasks_dir = project_dir / "delegation" / "tasks"
    task_id_upper = task_id.upper()
    for folder in tasks_dir.iterdir():
        if not folder.is_dir():
            continue
        for file in folder.glob("*.md"):
            name_upper = file.name.upper()
            if name_upper.startswith(task_id_upper):
                rest = name_upper[len(task_id_upper):]
                if not rest or not rest[0].isdigit():
                    return file
    return None
```

**Key change**: Instead of `task_id_upper in file.name.upper()` (substring),
uses `startswith` + boundary check. The boundary check ensures the character
after the matched ID is not a digit, preventing `ADV-1` from matching
`ADV-10-some-task.md`.

## Verification

```bash
# Should find the exact task
./scripts/core/project list | grep ADV-0045

# Should NOT match ADV-0040 when searching for ADV-4
# (test manually: search for a short ID that's a prefix of another)
```

## PR Template

```
Title: fix: Boundary-aware task ID matching in find_task_file (ADV-0048)

Body:
## Summary
Fixes find_task_file to use boundary-aware matching instead of substring
matching. Prevents ADV-1 from incorrectly matching ADV-10, ADV-11, etc.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] find_task_file uses `startswith` + boundary check (not `in`)
- [ ] `./scripts/core/project list` works correctly
- [ ] `./scripts/core/project complete` works on exact task IDs
- [ ] CI passes
- [ ] PR created and merged
