# ADV-0048: Upstream Sync — scripts/project Patch

**Status**: Todo
**Priority**: High
**Type**: Upstream Sync
**Estimated Effort**: 25 minutes
**Created**: 2026-03-07
**Parent**: ADV-0039
**Upstream Commit**: agentive-starter-kit@0c68f0f
**Depends On**: None (can be done independently)

## Summary

Update `scripts/project` with upstream version, then patch back our
boundary-aware `find_task_file` function. This is the most integration-heavy
script in the sync.

## Scope

### What Upstream Adds

The upstream version adds several new capabilities:
- `setup` subcommand (venv creation, dependency installation)
- `install-evaluators` subcommand
- `uv` detection and support
- Identity leak verification (`_verify_identity_leaks`)
- Better error handling throughout

### Our Patch: `find_task_file`

We must preserve our boundary-aware task file matching. The upstream version
uses simple `startswith()` which causes ADV-1 to match ADV-10, ADV-11, etc.

Our version:

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

### Integration Steps

1. Copy upstream `scripts/project` to replace ours
2. Find the `find_task_file` function
3. Replace it with our boundary-aware version above
4. Verify all `./scripts/project` subcommands still work

### Bot Findings (From PR #34)

CodeRabbit raised several findings about scripts/project:
- Line 448: Broaden Phase 2 identity replacements
- Line 615: Check for existing .venv before rejecting Python 3.13
- Line 809: --ref ignored when evaluators already installed
- Line 879: Reinstalls can leave deleted providers behind
- Line 1290: Identity leak verification trips on help banner

**All are upstream concerns** except that we should verify the identity leak
check doesn't false-positive on our project name.

## PR Template

```
Title: sync: Update scripts/project with boundary-aware find_task_file (ADV-0048)

Body:
## Summary
Updates scripts/project from upstream (adds setup, install-evaluators,
uv detection). Preserves our boundary-aware find_task_file patch to
prevent ADV-1 matching ADV-10/ADV-11.

Part of ADV-0039 (upstream sync).
```

## Acceptance Criteria

- [ ] scripts/project updated with upstream version
- [ ] find_task_file has boundary-aware matching
- [ ] `./scripts/project start ADV-0040` works correctly
- [ ] `./scripts/project start ADV-4` does NOT match ADV-0040
- [ ] CI passes
- [ ] PR created and merged
