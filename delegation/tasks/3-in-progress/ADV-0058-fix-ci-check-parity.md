# ADV-0058: Fix ci-check.sh / GitHub Actions Parity

**Status**: In Progress
**Priority**: High
**Type**: Bug Fix
**Estimated Effort**: 1 hour
**Created**: 2026-03-15
**Part Of**: Quality Gate Alignment (ADV-0058, ADV-0059, ADV-0060)

## Architectural Context

We have four quality gate layers that should form a coherent pipeline:

```
Pre-commit  ⊂  ci-check.sh  ≈  GitHub Actions  ⊂  Preflight
(fast)         (comprehensive)   (authoritative)    (workflow)
```

**Principle**: Each layer should be a strict subset of the next. If ci-check.sh
passes, GitHub Actions should pass. Currently they disagree on coverage thresholds,
lint scope, and path triggers.

This task fixes Layer 2 (ci-check.sh) to mirror Layer 3 (GitHub Actions). ADV-0059
then fixes Layer 3 to cover script changes. ADV-0060 fixes Layer 4 (preflight).

**Evidence**: 4 of 6 retros (ADV-0043, ADV-0045, ADV-0046, ADV-0054) flagged
ci-check.sh false failures. Agents waste time every session diagnosing and working
around it.

## Problems

### 1. Coverage threshold mismatch (causes exit 1 every run)

**ci-check.sh** (line 91):
```bash
pytest tests/ -v --cov=adversarial_workflow --cov-report=term-missing --cov-fail-under=80
```

**GitHub Actions** (`test-package.yml` line 221):
```bash
pytest tests/ -v --cov=adversarial_workflow --cov-report=xml --cov-report=term-missing
```

GitHub Actions does NOT enforce `--cov-fail-under`. Coverage is reported to Codecov
but doesn't gate the build (`fail_ci_if_error: false`). Current coverage is 64.44%,
so ci-check.sh **always fails**.

**Fix**: Remove `--cov-fail-under=80` from ci-check.sh. Coverage enforcement belongs
in Codecov config, not a local script.

### 2. Pattern lint scope mismatch

| Layer | Scope | Result |
|-------|-------|--------|
| Pre-commit | `adversarial_workflow/` | ✅ Passes |
| ci-check.sh | `scripts/ tests/` | Lints wrong dirs, skips main package |
| GitHub Actions | Not run | N/A |

ci-check.sh lints `scripts/` and `tests/` but NOT `adversarial_workflow/` — the
exact opposite of pre-commit (the authoritative scope).

**Fix**: Change ci-check.sh to lint `adversarial_workflow/` (matching pre-commit).

### 3. Unquoted `$PY_FILES` (minor)

Line 75 passes `$PY_FILES` unquoted to pattern_lint, which causes word-splitting
on filenames with spaces.

**Fix**: Use `find ... -print0 | xargs -0` or quote properly.

### 4. Permission system blocks agent workflow

`SKIP_TESTS=1 git commit` gets denied by the permission system (ADV-0045 retro,
multiple occurrences). This is the documented way to skip pre-commit tests for
config-only commits.

**Fix**: Add `Bash(SKIP_TESTS=1 *)` to `.claude/settings.json` allow list.

## Acceptance Criteria

- [ ] ci-check.sh coverage step matches GitHub Actions (no `--cov-fail-under`)
- [ ] ci-check.sh pattern lint scope matches pre-commit (`adversarial_workflow/`)
- [ ] ci-check.sh passes cleanly on current main (zero false failures)
- [ ] `$PY_FILES` properly handled (no word-splitting)
- [ ] `SKIP_TESTS=1 git commit` allowed in settings.json
- [ ] All 493 tests still pass
- [ ] ci-check.sh header comment accurately describes what it checks

## Files to Modify

1. `scripts/core/ci-check.sh` — fixes 1, 2, 3
2. `.claude/settings.json` — fix 4

## Notes

- This is the highest-leverage task: every agent session hits this failure
- Current coverage (64.44%) is a separate concern — ADV-0034/0035/0036 track
  test coverage improvements
- DK002 cleanup in tests/ is NOT in scope — the fix is to align scope with
  pre-commit, not to clean up test violations
- The comment on line 7 ("mirrors GitHub Actions test.yml") should remain accurate
  after this fix — update it if the scope changes
