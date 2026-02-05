# ADV-0030: BugBot Fixes for v0.8.1

**Status**: In Review
**Priority**: High
**Estimated Effort**: 1-2 hours
**Source**: BugBot comments on PR #22
**Branch**: `fix/v0.8.1-bugbot-issues` (already created)

---

## Summary

Four bugs identified by Cursor BugBot on PR #22 need to be fixed for v0.8.1 patch release. These affect CI/CD usage and config robustness.

---

## Issues to Fix

### 1. Category confirmation blocks dry-run in non-TTY (MEDIUM)
**Location**: `adversarial_workflow/library/commands.py:409-414`
**BugBot ID**: r2770414329

**Problem**: When using `--category --dry-run` in a CI/CD pipeline (non-TTY), the command fails because the category confirmation prompt only checks `if not yes:` without considering `dry_run`.

**Current code**:
```python
if not yes:
    response = input("Proceed? [y/N]: ").strip().lower()
```

**Fix**: Change to:
```python
# Skip confirmation for --yes or --dry-run (dry-run makes no changes)
if not yes and not dry_run:
    response = input("Proceed? [y/N]: ").strip().lower()
```

---

### 2. Dry-run returns success when all previews fail (MEDIUM)
**Location**: `adversarial_workflow/library/commands.py:544-560`
**BugBot ID**: r2770414341

**Problem**: If all dry-run previews fail (e.g., network errors), the command still returns exit code 0 (success). CI pipelines can't detect preview failures.

**Current code**:
```python
if dry_run:
    print(f"{CYAN}Dry run complete. Use without --dry-run to install.{RESET}")
# falls through to return 0
```

**Fix**: Check `success_count` in dry-run mode:
```python
if dry_run:
    if success_count == 0 and len(evaluator_specs) > 0:
        print(f"{RED}Dry run failed: No evaluators could be previewed.{RESET}")
        return 1
    print(f"{CYAN}Dry run complete. {success_count} evaluator(s) previewed.{RESET}")
    return 0
```

---

### 3. Config crash on non-dict YAML structure (MEDIUM)
**Location**: `adversarial_workflow/library/config.py:41-43`
**BugBot ID**: r2770414385

**Problem**: If `.adversarial/config.yml` contains valid YAML but not a dictionary (e.g., a list or scalar), `data.get("library", {})` raises `AttributeError` which is not caught.

**Current code**:
```python
data = yaml.safe_load(f) or {}
lib_config = data.get("library", {})  # ← AttributeError if data is list
```

**Fix**: Add `AttributeError` to exception handler OR add type check:
```python
data = yaml.safe_load(f) or {}
if not isinstance(data, dict):
    data = {}  # Treat non-dict as empty config
lib_config = data.get("library", {})
```

---

### 4. Unused config fields (LOW)
**Location**: `adversarial_workflow/library/config.py:18-22, 74-76`
**BugBot ID**: r2770414349

**Problem**: `ref` and `enabled` fields are loaded from config but never used by `LibraryClient`. `ADVERSARIAL_LIBRARY_REF` env var is processed but ignored.

**Options**:
- **A) Wire up `ref`**: Pass to `LibraryClient` and use in URL construction
- **B) Remove dead code**: Remove unused fields (breaking if anyone relies on them)
- **C) Document for future**: Add TODO comment explaining these are reserved for future use

**Recommended**: Option A - wire up `ref` field to allow branch switching.

---

## Acceptance Criteria

- [ ] `adversarial library install --category quick-check --dry-run` works in non-TTY
- [ ] Dry-run returns exit code 1 when all previews fail
- [ ] Malformed config.yml (list/scalar) doesn't crash, uses defaults
- [ ] `ADVERSARIAL_LIBRARY_REF` env var actually switches branches (or is removed)
- [ ] All existing tests pass
- [ ] New tests for each fix

---

## Testing

### Manual Tests
```bash
# Test 1: Category + dry-run in non-TTY
echo "" | adversarial library install --category quick-check --dry-run

# Test 2: Dry-run with invalid evaluator (should return 1)
adversarial library install nonexistent/evaluator --dry-run
echo $?  # Should be 1

# Test 3: Malformed config
echo '["invalid", "config"]' > .adversarial/config.yml
adversarial library list  # Should work, not crash
rm .adversarial/config.yml
```

### Unit Tests to Add
```python
# tests/test_library_enhancements.py
def test_category_dry_run_no_prompt(): ...
def test_dry_run_returns_error_on_all_failures(): ...
def test_config_handles_non_dict_yaml(): ...
def test_library_ref_env_var_used(): ...  # If wiring up ref
```

---

## References

- PR #22: https://github.com/movito/adversarial-workflow/pull/22
- BugBot comments: r2770414329, r2770414341, r2770414349, r2770414385
- Branch: `fix/v0.8.1-bugbot-issues`
