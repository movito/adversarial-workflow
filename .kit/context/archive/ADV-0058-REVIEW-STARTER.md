# ADV-0058 Review Starter

**PR**: https://github.com/movito/adversarial-workflow/pull/50
**Branch**: `feature/ADV-0058-fix-ci-check-parity`
**Task**: Fix ci-check.sh / GitHub Actions Parity

## What Changed

2 files modified, 1 backlog task created:

### `scripts/core/ci-check.sh`
- Removed `--cov-fail-under=80` (GitHub Actions doesn't enforce coverage threshold)
- Changed pattern lint scope from `scripts/ tests/` to `adversarial_workflow/` (matches pre-commit)
- Fixed unquoted `$PY_FILES` with `find -print0 | xargs -0`
- Made pattern lint advisory (non-blocking) — 34 pre-existing DK002 violations tracked in ADV-0061
- Added directory existence guard for `adversarial_workflow/`
- Updated header comment to accurately describe checks

### `.claude/settings.json`
- Added `Bash(SKIP_TESTS=1 git *)` to allow list (scoped to git only per BugBot review)

### `delegation/tasks/1-backlog/ADV-0061-fix-dk002-adversarial-workflow.md` (new)
- Backlog task to fix 34 DK002 violations and promote pattern lint back to blocking

## Key Design Decision

Pattern lint is **advisory** (warn, not fail) because:
1. GitHub Actions doesn't run pattern lint at all
2. Pre-commit gates it for staged files
3. 34 pre-existing violations would cause false failures
4. ADV-0061 tracks the cleanup; once done, lint becomes blocking again

## Review Focus Areas

1. Is the advisory pattern lint approach acceptable until ADV-0061?
2. Is `SKIP_TESTS=1 git *` sufficiently scoped? (BugBot flagged the original `SKIP_TESTS=1 *`)

## Bot Review

- **Round 1**: 3 threads — 1 High (permission scope), 1 Low (missing dir guard), 1 Trivial (doc fix). All fixed.
- **Round 2**: Clean — no new threads.
- **CodeRabbit**: APPROVED
- **BugBot**: No remaining findings

## CI Note

GitHub Actions did not trigger — `test-package.yml` paths filter only includes
`adversarial_workflow/`, `tests/`, `pyproject.toml`. This PR changes `scripts/` and
`.claude/`. ADV-0059 will add `scripts/` to the paths trigger. Locally verified:
493 tests pass, ci-check.sh exits 0.

## Verification

```bash
./scripts/core/ci-check.sh   # exits 0, 493 tests pass
```
