# ADV-0022: Fix check() .env Variable Count

**Status**: Todo
**Priority**: High
**Type**: Bug Fix
**Created**: 2025-01-23

## Problem

The `check()` command reports "0 variables" even when `.env` file has multiple variables configured:

```
✅ .env file found and loaded (0 variables)
```

This is confusing because the variables ARE loaded and available - it just reports the wrong count.

## Root Cause

The current implementation (lines 808-816 of cli.py) counts **new keys** added to the environment:

```python
env_keys_before = set(os.environ.keys())
load_dotenv(env_file)
env_keys_after = set(os.environ.keys())
new_keys = env_keys_after - env_keys_before
# Reports len(new_keys) which is 0 when main() already loaded .env
```

Since `main()` already calls `load_dotenv()` at startup (ADV-0021), the keys are already in the environment when `check()` runs. The second `load_dotenv()` call doesn't add any *new* keys.

## Solution

Use `dotenv_values()` to read the file directly and count variables:

```python
from dotenv import load_dotenv, dotenv_values

# In check() function, around line 803-828:
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
        issues.append({...})
    except PermissionError:
        issues.append({...})
    except OSError as e:
        issues.append({...})
```

## Files to Modify

1. `adversarial_workflow/cli.py`
   - Import `dotenv_values` from dotenv
   - Update check() function (lines 803-828) to use `dotenv_values()`
   - Use specific exception types instead of generic `Exception`

## Test Coverage

Tests already exist in `tests/test_env_loading.py`:
- `TestCheckEnvCount::test_check_reports_correct_env_count` - expects "3 variables"
- `TestCheckEnvCount::test_check_handles_empty_env_file` - expects "0 variables"
- `TestCheckEnvCount::test_check_handles_comments_in_env` - expects "2 variables"
- `TestCheckEnvCount::test_check_handles_unusual_env_entries` - expects "3 variables"

**Note**: Tests currently FAIL because feature is not implemented.

## Acceptance Criteria

1. [ ] `dotenv_values` imported from dotenv
2. [ ] check() uses `dotenv_values()` to count variables
3. [ ] All 4 TestCheckEnvCount tests pass
4. [ ] No regression in other tests
5. [ ] check() reports correct count even when main() already loaded .env

## Testing

```bash
# Run specific test class
.venv/bin/python -m pytest tests/test_env_loading.py::TestCheckEnvCount -v

# Full test suite
.venv/bin/python -m pytest tests/ -v
```

## Notes

- This is a regression from ADV-0021 which added `load_dotenv()` at startup
- PR #12 commit message claimed this was fixed but implementation was incomplete
- The `dotenv_values()` approach is more reliable since it reads the file directly
