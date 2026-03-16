# ADV-0061: Fix DK002 Violations in adversarial_workflow/

**Status**: Backlog
**Priority**: Medium
**Type**: Chore
**Estimated Effort**: 1 hour
**Created**: 2026-03-16
**Depends On**: ADV-0058 (ci-check.sh parity)

## Context

ADV-0058 aligned ci-check.sh pattern lint scope with pre-commit (`adversarial_workflow/`),
but discovered 34 pre-existing DK002 violations (missing `encoding="utf-8"` on `open()`,
`.read_text()`, `.write_text()` calls). Pattern lint was made advisory in ci-check.sh
as a workaround. Once these violations are fixed, pattern lint can be promoted back to
blocking.

## Problems

34 DK002 violations across 5 files:

| File | Count | Type |
|------|-------|------|
| `adversarial_workflow/cli.py` | 26 | `open()` without `encoding=` |
| `adversarial_workflow/cli.py` | 1 | DK004: bare `except Exception` with pass |
| `adversarial_workflow/evaluators/runner.py` | 3 | `open()`, `.read_text()`, `.write_text()` |
| `adversarial_workflow/utils/citations.py` | 2 | `open()` without `encoding=` |
| `adversarial_workflow/utils/config.py` | 1 | `open()` without `encoding=` |
| `adversarial_workflow/utils/validation.py` | 1 | `.write_text()` without `encoding=` |

## Acceptance Criteria

- [ ] All DK002 violations in `adversarial_workflow/` resolved (add `encoding="utf-8"`)
- [ ] DK004 in `cli.py:1026` resolved (add logging or `# noqa: DK004` with justification)
- [ ] `find adversarial_workflow/ -name '*.py' -print0 | xargs -0 python3 scripts/core/pattern_lint.py` exits 0
- [ ] Pattern lint step in ci-check.sh promoted from advisory back to blocking
- [ ] All tests still pass

## Files to Modify

1. `adversarial_workflow/cli.py` — 27 violations
2. `adversarial_workflow/evaluators/runner.py` — 3 violations
3. `adversarial_workflow/utils/citations.py` — 2 violations
4. `adversarial_workflow/utils/config.py` — 1 violation
5. `adversarial_workflow/utils/validation.py` — 1 violation
6. `scripts/core/ci-check.sh` — promote pattern lint back to blocking

## Notes

- All DK002 fixes are mechanical: add `encoding="utf-8"` parameter
- `cli.py` is 2600+ lines — high-diff but low-risk
- The DK004 in `cli.py:1026` needs investigation — may be intentional error suppression
- Once done, ci-check.sh pattern lint can set `FAILED=1` again on violations
