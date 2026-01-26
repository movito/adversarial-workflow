# ADV-0023: Exception Handling Improvements for .env Loading

## Summary

Bot reviews (CodeRabbit, Cursor Bugbot) identified two high-severity exception handling gaps in the .env loading code introduced by ADV-0021/ADV-0022.

## Issues Identified

### 1. UnicodeDecodeError Not Caught in check() (High Severity)

**Location**: `adversarial_workflow/cli.py` lines 815-833

**Problem**: The `check()` function's exception handling for `dotenv_values()` only catches `FileNotFoundError`, `PermissionError`, and `OSError`, but won't catch `UnicodeDecodeError` (a `ValueError` subclass) when `.env` files contain invalid UTF-8.

**Impact**: The `check` command crashes instead of gracefully reporting the encoding issue. This is a regression from the previous code which caught all exceptions with `except Exception`.

**Fix**: Add `ValueError` to the exception handling chain (covers `UnicodeDecodeError`).

### 2. Unhandled Exception in main() load_dotenv() (High Severity)

**Location**: `adversarial_workflow/cli.py` lines 2881-2882

**Problem**: The `load_dotenv()` call in `main()` has no exception handling. If the `.env` file contains invalid UTF-8 or other encoding issues, `load_dotenv()` raises `UnicodeDecodeError`, crashing the entire CLI before any command can execute.

**Impact**: Users cannot even run `adversarial --help` or `adversarial --version` when their `.env` file has encoding problems, making the tool completely unusable.

**Fix**: Wrap `load_dotenv()` in try/except and print a warning instead of crashing.

## Implementation

### Fix 1: check() Exception Handling

```python
# Before
except (FileNotFoundError, PermissionError) as e:
    ...
except OSError as e:
    ...

# After
except (FileNotFoundError, PermissionError) as e:
    ...
except (OSError, ValueError) as e:
    # Covers UnicodeDecodeError (ValueError subclass) and other OS errors
    ...
```

### Fix 2: main() Exception Handling

```python
# Before
load_dotenv()

# After
try:
    load_dotenv()
except Exception as e:
    # Don't crash CLI for .env issues - commands may not need it
    import sys
    print(f"Warning: Could not load .env file: {e}", file=sys.stderr)
```

## Related

- Parent: ADV-0021 (Load .env at startup)
- Parent: ADV-0022 (Fix check() variable count)
- PR: #12

## Acceptance Criteria

- [ ] `UnicodeDecodeError` in .env file doesn't crash `check` command
- [ ] `UnicodeDecodeError` in .env file doesn't crash CLI startup
- [ ] Users can still run `--help` and `--version` with malformed .env
- [ ] Warning message printed when .env can't be loaded
- [ ] All existing tests pass
