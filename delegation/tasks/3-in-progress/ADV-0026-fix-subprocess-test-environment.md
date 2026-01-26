# ADV-0026: Fix Subprocess Test Environment Issues

**Status**: In Progress
**Priority**: High
**Type**: Bug Fix
**Created**: 2025-01-23

## Problem

Tests in `tests/test_env_loading.py` fail when run with system pytest because:

1. `sys.executable` points to pytest's Python (`/opt/homebrew/Cellar/pytest/8.4.2/libexec/bin/python`)
2. That Python environment doesn't have `adversarial_workflow` installed
3. All subprocess-based tests get `ModuleNotFoundError: No module named 'adversarial_workflow'`

**Error example**:
```
E       AssertionError: Expected OPENAI_API_KEY check. stdout: , stderr: /opt/homebrew/Cellar/pytest/8.4.2/libexec/bin/python: Error while finding module specification for 'adversarial_workflow.cli' (ModuleNotFoundError: No module named 'adversarial_workflow')
```

## Affected Tests

All 11 tests in `tests/test_env_loading.py`:
- `TestEnvFileLoading` (4 tests)
- `TestCheckEnvCount` (4 tests)
- `TestCustomEvaluatorEnvLoading` (1 test)
- `TestEvaluatorConflictWarning` (2 tests)

## Root Cause

The tests use `subprocess.run([sys.executable, "-m", "adversarial_workflow.cli", ...])` which depends on `sys.executable` pointing to a Python with the package installed.

## Proposed Solutions

### Option A: Use `python -m adversarial_workflow.cli` with PATH lookup (Recommended)
```python
# Instead of:
subprocess.run([sys.executable, "-m", "adversarial_workflow.cli", ...])

# Use:
subprocess.run(["python", "-m", "adversarial_workflow.cli", ...])
# Or use 'adversarial' command directly if installed
subprocess.run(["adversarial", "check"], ...)
```

### Option B: Add pytest configuration to use correct Python
Add to `conftest.py`:
```python
import sys
import os

@pytest.fixture(autouse=True)
def ensure_correct_python():
    """Ensure subprocess tests use the correct Python interpreter."""
    # Could set PYTHON_PATH or use subprocess with explicit path
    pass
```

### Option C: Skip tests if package not installed in current Python
```python
import pytest
try:
    import adversarial_workflow
except ImportError:
    pytest.skip("adversarial_workflow not installed in current Python")
```

## Acceptance Criteria

1. [ ] All tests in `tests/test_env_loading.py` pass when run with:
   - `pytest tests/test_env_loading.py`
   - `python -m pytest tests/test_env_loading.py`
2. [ ] Tests work in CI environment (GitHub Actions)
3. [ ] Tests work with both system pytest and virtual environment pytest
4. [ ] No changes to actual CLI functionality

## Testing

```bash
# Run with system pytest
pytest tests/test_env_loading.py -v

# Run with python -m pytest
python -m pytest tests/test_env_loading.py -v

# Verify full test suite still passes
pytest tests/ -v
```

## Notes

- This is a test infrastructure issue, not a functional bug
- The actual CLI functionality (ADV-0021 through ADV-0025) works correctly
- Issue surfaced during PR #13 merge for v0.6.2
