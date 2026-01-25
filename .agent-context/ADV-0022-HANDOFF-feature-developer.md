# ADV-0022 Task Starter

## Quick Context

The `check()` command reports "0 variables" for `.env` files even when they contain multiple variables. This happens because `main()` already loads the `.env` at startup, so when `check()` calls `load_dotenv()` again, no *new* keys are added.

**Fix**: Use `dotenv_values()` to read the file directly and count variables.

**Branch**: `fix/adv-0024-0025-env-loading-v2` (continue on current branch)
**Tests**: Already exist and currently FAIL - your job is to make them pass

## Current Code (lines 803-824)

```python
# adversarial_workflow/cli.py, check() function

# Check for .env file first (before loading environment variables)
env_file = Path(".env")
env_loaded = False
env_keys_before = set(os.environ.keys())  # <-- Problem: counts NEW keys only

if env_file.exists():
    try:
        load_dotenv(env_file)
        env_keys_after = set(os.environ.keys())
        new_keys = env_keys_after - env_keys_before  # <-- Always 0 if already loaded
        env_loaded = True
        good_checks.append(
            f".env file found and loaded ({len(new_keys)} variables)"  # <-- Reports 0
        )
    except Exception as e:  # <-- Too broad
        issues.append({...})
```

## Required Changes

### 1. Add import at top of file

Find the existing `from dotenv import load_dotenv` and add `dotenv_values`:

```python
from dotenv import load_dotenv, dotenv_values
```

### 2. Replace lines 803-824 with:

```python
    # Check for .env file first (before loading environment variables)
    env_file = Path(".env")
    env_loaded = False

    if env_file.exists():
        try:
            # Count variables by reading file directly (works even if already loaded)
            env_vars = dotenv_values(env_file)
            var_count = len([k for k, v in env_vars.items() if v is not None])

            # Still load to ensure environment is set
            load_dotenv(env_file)
            env_loaded = True
            good_checks.append(
                f".env file found and loaded ({var_count} variables)"
            )
        except FileNotFoundError:
            issues.append(
                {
                    "severity": "WARNING",
                    "message": ".env file disappeared during check",
                    "fix": "Ensure .env file exists and is readable",
                }
            )
        except PermissionError:
            issues.append(
                {
                    "severity": "WARNING",
                    "message": ".env file found but permission denied",
                    "fix": "Check file permissions: chmod 644 .env",
                }
            )
        except OSError as e:
            issues.append(
                {
                    "severity": "WARNING",
                    "message": f".env file found but could not be loaded: {e}",
                    "fix": "Check .env file format and permissions",
                }
            )
```

**Key changes**:
1. Remove `env_keys_before` tracking (no longer needed)
2. Use `dotenv_values()` to read file and count variables
3. Filter out `None` values: `if v is not None`
4. Use specific exception types instead of generic `Exception`

## Testing

```bash
# Run the 4 specific tests (currently FAIL, should PASS after fix)
.venv/bin/python -m pytest tests/test_env_loading.py::TestCheckEnvCount -v

# Expected output after fix:
# test_check_reports_correct_env_count PASSED     - expects "3 variables"
# test_check_handles_empty_env_file PASSED        - expects "0 variables"
# test_check_handles_comments_in_env PASSED       - expects "2 variables"
# test_check_handles_unusual_env_entries PASSED   - expects "3 variables"

# Run full test suite to check for regressions
.venv/bin/python -m pytest tests/ -v
```

## Manual Verification

```bash
# Create test .env
echo -e "KEY1=value1\nKEY2=value2\nKEY3=value3" > /tmp/test-env/.env
cd /tmp/test-env
adversarial check

# Should show: ✅ .env file found and loaded (3 variables)
# NOT: ✅ .env file found and loaded (0 variables)
```

## Acceptance Criteria

- [ ] `dotenv_values` imported from dotenv
- [ ] `check()` uses `dotenv_values()` to count variables
- [ ] All 4 `TestCheckEnvCount` tests pass
- [ ] No regression in other tests
- [ ] Specific exception types (not generic `Exception`)

## Resources

- **Task spec**: `delegation/tasks/2-todo/ADV-0022-check-env-variable-count.md`
- **Test file**: `tests/test_env_loading.py` (class `TestCheckEnvCount`)
- **CLI file**: `adversarial_workflow/cli.py` (function `check()`, lines 803-824)
