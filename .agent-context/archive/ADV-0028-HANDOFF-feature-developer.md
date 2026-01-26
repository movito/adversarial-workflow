# ADV-0028 Task Starter

## Quick Context

Fix three issues in `scripts/project` identified by CodeRabbit and Bugbot during code review. The most important is a substring matching bug that could match wrong task files.

**Branch**: Create `fix/adv-0028-scripts-project-fixes`
**Base**: `main`
**Priority**: Issue 2 (substring bug) > Issue 1 (dead code) > Issue 3 (optional refactor)

## Issue 1: Dead Code - CalledProcessError Handler (Low)

**Location**: `scripts/project` lines 614-619

### Problem

`subprocess.run()` without `check=True` never raises `CalledProcessError`. The exception handler is unreachable.

### Current Code

```python
try:
    result = subprocess.run(cmd, cwd=project_dir)
    sys.exit(result.returncode)
except subprocess.CalledProcessError as e:  # DEAD CODE - never executes
    print(f"❌ Error running command: {e}")
    sys.exit(1)
```

### Fix

Remove the try/except entirely:

```python
result = subprocess.run(cmd, cwd=project_dir)
sys.exit(result.returncode)
```

---

## Issue 2: Substring Matching Bug in find_task_file (Medium) ⚠️

**Location**: `scripts/project` line 57

### Problem

```python
# Current (buggy):
if task_id_upper in file.name.upper():
```

Searching for `ADV-1` matches:
- ✅ `ADV-1-some-task.md` (correct)
- ❌ `ADV-10-other-task.md` (wrong!)
- ❌ `ADV-100-another.md` (wrong!)
- ❌ `ADV-11-foo.md` (wrong!)

### Fix

Use boundary-aware matching. The task ID should be followed by a non-digit character:

```python
import re

def find_task_file(task_id: str, tasks_dir: Path) -> Optional[Path]:
    """Find task file by ID with exact matching."""
    task_id_upper = task_id.upper()

    # Pattern: task ID followed by non-digit (- or . or end of string)
    # This prevents ADV-1 from matching ADV-10, ADV-11, etc.
    pattern = re.compile(rf'^{re.escape(task_id_upper)}(?!\d)', re.IGNORECASE)

    for folder in tasks_dir.iterdir():
        if folder.is_dir():
            for file in folder.glob("*.md"):
                if pattern.match(file.name):
                    return file
    return None
```

**Alternative simpler fix** (if regex feels heavy):

```python
def find_task_file(task_id: str, tasks_dir: Path) -> Optional[Path]:
    """Find task file by ID with exact matching."""
    task_id_upper = task_id.upper()

    for folder in tasks_dir.iterdir():
        if folder.is_dir():
            for file in folder.glob("*.md"):
                name_upper = file.name.upper()
                # Must start with task ID followed by non-digit
                if name_upper.startswith(task_id_upper):
                    # Check next char is not a digit
                    rest = name_upper[len(task_id_upper):]
                    if rest and not rest[0].isdigit():
                        return file
                    elif not rest:  # Exact match (unlikely but handle it)
                        return file
    return None
```

### Test Cases

After fixing, verify:
```bash
# Create test files
mkdir -p /tmp/test-tasks/2-todo
touch /tmp/test-tasks/2-todo/ADV-1-first-task.md
touch /tmp/test-tasks/2-todo/ADV-10-tenth-task.md
touch /tmp/test-tasks/2-todo/ADV-100-hundredth.md

# Test (manually or add unit test)
# find_task_file("ADV-1", ...) should return ADV-1-first-task.md, NOT ADV-10 or ADV-100
```

---

## Issue 3: Inline Python Blocks (Optional/Trivial)

**Location**: `scripts/project` lines 295-362

Large inline Python passed via `python -c` is hard to maintain. This is optional for this PR.

### If You Want to Fix It

Extract to separate files:
- `scripts/linear_teams.py` (~70 lines)
- `scripts/linear_sync_status.py` (~180 lines)

Then call them:
```python
subprocess.run([sys.executable, str(scripts_dir / "linear_teams.py"), ...])
```

**Recommendation**: Skip this for now. It's a larger refactor and not critical.

---

## Implementation Order

1. **Fix Issue 2 first** (substring bug) - this is the real bug
2. **Fix Issue 1** (dead code) - quick cleanup
3. **Skip Issue 3** unless you have time - optional refactor

## Files to Modify

| File | Changes |
|------|---------|
| `scripts/project` | Fix `find_task_file()` (line ~57), remove dead code (lines 614-619) |

## Create Branch

```bash
git checkout main
git pull origin main
git checkout -b fix/adv-0028-scripts-project-fixes
```

## Testing

```bash
# After making changes, test manually:
./scripts/project task ADV-1   # Should find ADV-1, NOT ADV-10

# Run full test suite
.venv/bin/python -m pytest tests/ -v

# If you add unit tests for find_task_file:
.venv/bin/python -m pytest tests/test_scripts_project.py -v
```

## Acceptance Criteria

- [ ] `find_task_file()` uses exact/boundary-aware matching
- [ ] `ADV-1` does NOT match `ADV-10`, `ADV-11`, `ADV-100`, etc.
- [ ] Dead CalledProcessError handler removed
- [ ] All existing tests pass
- [ ] (Optional) Unit test for `find_task_file()` edge cases

## Commit Message

```
fix(scripts): Fix substring matching bug and remove dead code (ADV-0028)

- find_task_file() now uses boundary-aware matching
- ADV-1 no longer incorrectly matches ADV-10, ADV-11, etc.
- Remove unreachable CalledProcessError exception handler

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

## Resources

- **Task spec**: `delegation/tasks/1-backlog/ADV-0028-scripts-project-fixes.md`
- **File to fix**: `scripts/project`
- **Found by**: CodeRabbit, Bugbot automated reviews
