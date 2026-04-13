# ADV-0061 Review Starter

**PR**: #53
**Branch**: `feature/ADV-0061-fix-dk002-violations`
**Type**: Chore (mechanical)
**Risk**: Low -- no behavior change, no new logic

## Summary

Resolves all 34 DK violations in `adversarial_workflow/` and promotes pattern lint
from advisory to blocking in both ci-check.sh and GitHub Actions.

## Changes

| File | Change | Count |
|------|--------|-------|
| `adversarial_workflow/cli.py` | Add `encoding="utf-8"` to `open()` calls | 26 |
| `adversarial_workflow/cli.py` | Add `# noqa: DK004` to fire-and-forget except | 1 |
| `adversarial_workflow/evaluators/runner.py` | Add `encoding="utf-8"` to I/O calls | 3 |
| `adversarial_workflow/utils/citations.py` | Add `encoding="utf-8"` to `open()` calls | 2 |
| `adversarial_workflow/utils/config.py` | Add `encoding="utf-8"` to `open()` call | 1 |
| `adversarial_workflow/utils/validation.py` | Add `encoding="utf-8"` to `.write_text()` | 1 |
| `scripts/core/ci-check.sh` | Promote pattern lint from advisory to blocking | - |
| `.github/workflows/test-package.yml` | Remove `continue-on-error: true` from pattern lint | - |

## Review Focus

1. **Spot-check encoding additions**: Verify `encoding="utf-8"` is placed correctly
   after the mode argument in `open()` calls (e.g., `open(path, "w", encoding="utf-8")`)
2. **DK004 noqa**: Verify the justification comment on cli.py line ~1026 is appropriate
   (fire-and-forget script version check)
3. **ci-check.sh**: Confirm pattern lint now sets `FAILED=1` on violations
4. **GitHub Actions**: Confirm `continue-on-error: true` is removed from pattern lint step

## Verification Commands

```bash
# Pattern lint clean:
find adversarial_workflow/ -name '*.py' -print0 | xargs -0 python3 scripts/core/pattern_lint.py

# Tests pass:
pytest tests/ -x -q

# Full CI:
./scripts/core/ci-check.sh
```

## Bot Review Status

- **CodeRabbit**: APPROVED (0 threads)
- **BugBot**: Clean (no findings)
- **Evaluator**: Skipped (mechanical task, zero design risk)
