# ADV-0026 Task Starter

## Quick Context

Tests using `subprocess.run([sys.executable, ...])` fail when run with system pytest because `sys.executable` points to pytest's Python, not the one with `adversarial_workflow` installed.

**Branch**: Create `fix/adv-0026-subprocess-test-env`
**Base**: `main`

## The Problem

```python
# Current code in tests:
subprocess.run([sys.executable, "-m", "adversarial_workflow.cli", "check"], ...)

# When run with system pytest:
# sys.executable = /opt/homebrew/Cellar/pytest/8.4.2/libexec/bin/python
# This Python doesn't have adversarial_workflow installed!
```

## Solution: Add `cli_python` Fixture

### Step 1: Add fixture to conftest.py

Add this fixture to `tests/conftest.py`:

```python
import shutil

@pytest.fixture
def cli_python():
    """Get Python interpreter path that has adversarial_workflow installed.

    When running with system pytest, sys.executable may point to a Python
    that doesn't have our package installed. This fixture finds the correct
    Python by checking if the 'adversarial' command is available.
    """
    # First, try to find the adversarial command on PATH
    adversarial_cmd = shutil.which("adversarial")
    if adversarial_cmd:
        # The adversarial script's shebang tells us which Python to use
        # But simpler: just use the command directly
        return None  # Signal to use "adversarial" command directly

    # Fall back to sys.executable (works in venv)
    return sys.executable


@pytest.fixture
def run_cli(cli_python):
    """Helper fixture to run CLI commands in subprocess.

    Usage:
        result = run_cli(["check"], cwd=tmp_path, env=env)
    """
    def _run_cli(args, **kwargs):
        if cli_python is None:
            # Use adversarial command directly
            cmd = ["adversarial"] + args
        else:
            # Use python -m
            cmd = [cli_python, "-m", "adversarial_workflow.cli"] + args

        return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

    return _run_cli
```

### Step 2: Update test_env_loading.py

Replace all `subprocess.run([sys.executable, ...])` calls with `run_cli` fixture.

**Before:**
```python
def test_env_var_available_via_cli_check(self, tmp_path):
    # ...
    result = subprocess.run(
        [sys.executable, "-m", "adversarial_workflow.cli", "check"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )
```

**After:**
```python
def test_env_var_available_via_cli_check(self, tmp_path, run_cli):
    # ...
    result = run_cli(["check"], cwd=tmp_path, env=env)
```

### Step 3: Update other affected test files

Same pattern for:
- `tests/test_cli.py`
- `tests/test_cli_dynamic_commands.py`
- `tests/test_list_evaluators.py`

## Files to Modify

| File | Changes |
|------|---------|
| `tests/conftest.py` | Add `cli_python` and `run_cli` fixtures |
| `tests/test_env_loading.py` | Use `run_cli` fixture (8 occurrences) |
| `tests/test_cli.py` | Use `run_cli` fixture |
| `tests/test_cli_dynamic_commands.py` | Use `run_cli` fixture |
| `tests/test_list_evaluators.py` | Use `run_cli` fixture |

## Testing

```bash
# Create branch
git checkout -b fix/adv-0026-subprocess-test-env

# Run tests with venv pytest (should pass)
.venv/bin/python -m pytest tests/test_env_loading.py -v

# Run tests with system pytest (should NOW pass too)
pytest tests/test_env_loading.py -v

# Full test suite
.venv/bin/python -m pytest tests/ -v
```

## Alternative: Simpler Approach

If the fixture approach seems complex, a simpler solution is to just use the `adversarial` command directly (assuming it's installed):

```python
# Instead of:
subprocess.run([sys.executable, "-m", "adversarial_workflow.cli", "check"], ...)

# Use:
subprocess.run(["adversarial", "check"], ...)
```

This works if the package is installed via `pip install -e .` and `adversarial` is on PATH.

## Acceptance Criteria

- [ ] `cli_python` and `run_cli` fixtures added to conftest.py
- [ ] All 4 test files updated to use `run_cli`
- [ ] Tests pass with `.venv/bin/python -m pytest`
- [ ] Tests pass with system `pytest` (if adversarial is on PATH)
- [ ] No changes to CLI functionality

## Resources

- **Task spec**: `delegation/tasks/2-todo/ADV-0026-fix-subprocess-test-environment.md`
- **Test files**: `tests/test_env_loading.py`, `tests/test_cli.py`, etc.
- **conftest.py**: `tests/conftest.py`
