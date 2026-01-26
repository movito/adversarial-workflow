# ADV-0028: Fix scripts/project Issues

**Status**: Backlog
**Priority**: Medium
**Type**: Bug Fix / Code Quality
**Created**: 2025-01-25
**Reported By**: feature-developer (via CodeRabbit, Bugbot)

## Summary

Three issues identified in `scripts/project` during ADV-0026 work:

1. Dead code in CalledProcessError handler
2. Substring matching bug in `find_task_file()`
3. Inline Python blocks hard to maintain

## Issues

### Issue 1: Dead Code - CalledProcessError Handler (Low Severity)

**Location**: `scripts/project` lines 614-619

`subprocess.run()` is called without `check=True`, so it never raises `CalledProcessError`. The exception handler is unreachable dead code.

```python
# Current (dead code):
try:
    result = subprocess.run(cmd, cwd=project_dir)
    sys.exit(result.returncode)
except subprocess.CalledProcessError as e:  # Never executes
    print(f"❌ Error running command: {e}")
    sys.exit(1)
```

**Fix**: Remove the dead `except subprocess.CalledProcessError` block.

```python
# Fixed:
result = subprocess.run(cmd, cwd=project_dir)
sys.exit(result.returncode)
```

---

### Issue 2: Substring Matching Bug in find_task_file (Medium Severity)

**Location**: `scripts/project` line 57

The `find_task_file` function uses substring matching (`task_id_upper in file.name.upper()`) which can match wrong files. For example, searching for "ADV-1" would also match "ADV-10", "ADV-11", etc.

**Example**:
```python
# Current (buggy):
if task_id_upper in file.name.upper():
    # "ADV-1" matches "ADV-1-task.md" BUT ALSO "ADV-10-task.md", "ADV-100-task.md"
```

**Fix**: Use exact matching or boundary-aware matching:

```python
# Option A: Regex with word boundary
import re
pattern = rf'\b{re.escape(task_id_upper)}\b'
if re.search(pattern, file.name.upper()):
    ...

# Option B: Check for delimiter after task ID
if file.name.upper().startswith(task_id_upper + "-") or \
   file.name.upper().startswith(task_id_upper + ".") or \
   file.name.upper() == task_id_upper + ".MD":
    ...
```

---

### Issue 3: Inline Python Blocks Hard to Maintain (Low/Trivial)

**Location**: `scripts/project` lines 295-362

Large inline Python code (~70 lines for teams, ~180 lines for sync-status) passed via `python -c` is difficult to maintain:
- No IDE support (syntax highlighting, linting, type checking)
- Cannot be unit tested independently
- Changes require careful string escaping

**Fix**: Extract to standalone scripts:
- `scripts/linear_teams.py`
- `scripts/linear_sync_status.py`

Then call them normally:
```python
subprocess.run([sys.executable, "scripts/linear_teams.py", ...])
```

## Acceptance Criteria

- [ ] Dead CalledProcessError handler removed
- [ ] `find_task_file()` uses exact/boundary-aware matching
- [ ] Tests added for `find_task_file()` edge cases (ADV-1 vs ADV-10)
- [ ] (Optional) Inline Python extracted to separate files
- [ ] All existing tests pass

## Testing

```bash
# Verify find_task_file doesn't match wrong files
./scripts/project task ADV-1  # Should NOT match ADV-10

# Run full test suite
.venv/bin/python -m pytest tests/ -v
```

## Notes

- Issue 2 (substring matching) is the highest priority - could cause incorrect task operations
- Issue 1 is trivial but should be cleaned up
- Issue 3 is optional but improves maintainability
- These issues came from agentive-starter-kit files copied in ADV-0027

## References

- Reported during: ADV-0026 implementation
- Found by: CodeRabbit, Bugbot automated reviews
- File: `scripts/project`
