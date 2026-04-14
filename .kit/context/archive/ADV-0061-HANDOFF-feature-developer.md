# ADV-0061 Handoff: Fix DK002 Violations in adversarial_workflow/

## Mission

Add `encoding="utf-8"` to all `open()`, `.read_text()`, and `.write_text()` calls in `adversarial_workflow/` that are missing it, suppress one DK004 with a noqa comment, then promote pattern lint from advisory to blocking in both ci-check.sh and GitHub Actions.

## Violation Inventory (34 total)

Run `find adversarial_workflow/ -name '*.py' -print0 | xargs -0 python3 scripts/core/pattern_lint.py` to see exact lines.

### By file

| File | Count | Rule |
|------|-------|------|
| `adversarial_workflow/cli.py` | 26 | DK002 |
| `adversarial_workflow/cli.py` | 1 | DK004 (line 1026) |
| `adversarial_workflow/evaluators/runner.py` | 3 | DK002 |
| `adversarial_workflow/utils/citations.py` | 2 | DK002 |
| `adversarial_workflow/utils/config.py` | 1 | DK002 |
| `adversarial_workflow/utils/validation.py` | 1 | DK002 |

### DK002 fix pattern

```python
# Before:
with open(path) as f:
content = path.read_text()
path.write_text(data)

# After:
with open(path, encoding="utf-8") as f:
content = path.read_text(encoding="utf-8")
path.write_text(data, encoding="utf-8")
```

For `open()` calls with a mode argument, insert `encoding="utf-8"` after the mode:
```python
# Before:
with open(path, "w") as f:
# After:
with open(path, "w", encoding="utf-8") as f:
```

### DK004 fix (line 1026 of cli.py)

```python
# Before:
except Exception:
    pass

# After:
except Exception:  # noqa: DK004 — fire-and-forget: script version check is best-effort
    pass
```

## Promote pattern lint to blocking

### ci-check.sh (2 changes)

1. **Line 12** — update comment:
   ```
   #   3. Pattern lint (DK rules)    (blocking)
   ```

2. **Lines 71-84** — replace advisory block with blocking:
   ```bash
   if find adversarial_workflow/ -name '*.py' -print0 2>/dev/null | xargs -0 python3 "$SCRIPT_DIR/pattern_lint.py" 2>&1; then
       echo "OK: Pattern lint: No DK violations"
   else
       echo "ERROR: Pattern lint: DK violations found"
       FAILED=1
   fi
   ```
   Remove the `NOTE: Advisory only` comment and the `WARN:` prefix.

### .github/workflows/test-package.yml (2 changes)

1. **Line 231** — rename step:
   ```yaml
   - name: Run pattern lint
   ```
   (remove "(advisory)")

2. **Line 233** — remove:
   ```yaml
   continue-on-error: true
   ```

## Verification

After all fixes:
```bash
# Must exit 0:
find adversarial_workflow/ -name '*.py' -print0 | xargs -0 python3 scripts/core/pattern_lint.py

# Must pass:
pytest tests/ -x -q

# Must pass:
./scripts/core/ci-check.sh
```

## Notes

- All DK002 fixes are mechanical — adding `encoding="utf-8"` makes explicit what Python 3 already defaults to on most platforms. No behavior change.
- `cli.py` is 2600+ lines so the diff will be large, but every change is identical.
- No new tests needed — existing 493 tests verify no regressions.
- Do NOT touch files outside `adversarial_workflow/`, `scripts/core/ci-check.sh`, and `.github/workflows/test-package.yml`.
