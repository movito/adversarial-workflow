# ADV-0059 Review Starter

**PR**: https://github.com/movito/adversarial-workflow/pull/51
**Branch**: `feature/ADV-0059-gh-actions-paths-alignment`
**Task**: ADV-0059 — GitHub Actions Paths Filter & CI Alignment

## What Changed

2 files modified, 4 commits:

1. **`.github/workflows/test-package.yml`** — Core change
   - Added `scripts/**`, `.pre-commit-config.yaml`, `.github/workflows/**` to paths filter (both push and pull_request triggers)
   - Added 3 lint steps to `test-pytest` job: ruff format, ruff lint, pattern lint (advisory)
   - Pattern lint uses `find | xargs` to expand directory into individual .py files

2. **`scripts/core/ci-check.sh`** — Header update
   - Documents the parity invariant: "if this script passes, GitHub Actions will pass"
   - Updated stale comment about pattern lint scope

## Key Decisions

- **Pattern lint is advisory** (`continue-on-error: true`) — matches ci-check.sh until ADV-0061 cleans up 34 DK002 violations
- **Ruff steps are blocking** — intentional safety net when pre-commit is bypassed
- **Self-validating PR**: This PR touches `.github/workflows/**`, which wouldn't have triggered CI before — CI triggering proves the paths filter works

## Bot Review Summary

- **BugBot**: 1 finding (High) — pattern_lint.py needs file paths not directory. Fixed.
- **CodeRabbit**: 2 findings (Minor) — task spec inconsistencies. Fixed. Final: APPROVED.
- **Threads**: 3 total, 3 resolved, 0 unresolved

## Review Focus Areas

1. Verify the paths filter covers the right files (no over-triggering)
2. Confirm `continue-on-error: true` for pattern lint is appropriate
3. Check that `find | xargs` invocation matches ci-check.sh behavior
