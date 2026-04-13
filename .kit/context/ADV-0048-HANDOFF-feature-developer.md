# ADV-0048 Handoff: fix find_task_file Boundary Matching

## Task

Fix the `find_task_file` function in `scripts/core/project` to use boundary-aware matching instead of substring matching.

## The Bug

Current code uses `if task_id_upper in file.name.upper()` which means searching for `ADV-1` matches `ADV-10`, `ADV-11`, `ADV-100`, etc.

## The Fix

In `scripts/core/project`, find the `find_task_file` function and replace it:

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

That's the entire change. Nothing else in the file needs modification.

## Implementation

```bash
# 1. Create branch
git checkout -b feature/ADV-0048-find-task-file-fix

# 2. Start task
./scripts/core/project start ADV-0048

# 3. Edit scripts/core/project — replace find_task_file function body

# 4. Verify
./scripts/core/project list
./scripts/core/project move ADV-0048 in-progress  # should already be there

# 5. Run CI
./scripts/core/ci-check.sh

# 6. Commit, push, create PR
```

## PR Details

**Title**: `fix: Boundary-aware task ID matching in find_task_file (ADV-0048)`

**Body**:
```
## Summary
Fixes find_task_file to use boundary-aware matching instead of substring
matching. Prevents ADV-1 from incorrectly matching ADV-10, ADV-11, etc.

Part of ADV-0039 (upstream sync).

## Test plan
- [ ] `./scripts/core/project list` works correctly
- [ ] `./scripts/core/project complete` works on exact task IDs
- [ ] CI passes
```
