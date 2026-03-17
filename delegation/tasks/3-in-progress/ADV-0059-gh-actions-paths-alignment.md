# ADV-0059: GitHub Actions Paths Filter & CI Alignment

**Status**: In Progress
**Priority**: Medium
**Type**: Enhancement
**Estimated Effort**: 1 hour
**Created**: 2026-03-15
**Depends On**: ADV-0058
**Part Of**: Quality Gate Alignment (ADV-0058, ADV-0059, ADV-0060)

## Architectural Context

Layer 3 (GitHub Actions) is the authoritative quality gate, but it has gaps:

1. Changes to `scripts/**` don't trigger CI at all — script bugs ship unvalidated
2. Changes to `.pre-commit-config.yaml` don't trigger CI
3. Changes to `.github/workflows/` don't trigger CI
4. No ruff or pattern_lint step — relies entirely on pre-commit (which agents
   can skip with `SKIP_TESTS=1`)

After ADV-0058 makes ci-check.sh a true mirror, this task ensures GitHub Actions
catches what ci-check.sh catches.

**Evidence**: ADV-0048 retro: "Changes to scripts/ don't trigger CI at all. Script
bugs can ship without any automated validation." ADV-0054 was a script bug that
shipped undetected.

## Changes

### 1. Expand paths filter in test-package.yml

**Current** (lines 6-15):
```yaml
paths:
  - 'adversarial_workflow/**'
  - 'tests/**'
  - 'pyproject.toml'
```

**Proposed**:
```yaml
paths:
  - 'adversarial_workflow/**'
  - 'tests/**'
  - 'scripts/**'
  - 'pyproject.toml'
  - '.pre-commit-config.yaml'
  - '.github/workflows/**'
```

This ensures CI runs when scripts, pre-commit config, or workflow definitions change.

### 2. Add ruff + pattern_lint steps to GitHub Actions

Currently GitHub Actions runs only pytest. Pre-commit handles formatting/linting,
but there's no CI enforcement if an agent bypasses pre-commit.

Add steps to the `test-pytest` job (after install, before pytest):

```yaml
- name: Check formatting with Ruff
  run: ruff format --check .

- name: Lint with Ruff
  run: ruff check .

- name: Run pattern lint
  run: python3 scripts/core/pattern_lint.py adversarial_workflow/
```

This makes GitHub Actions a superset of ci-check.sh (after ADV-0058 aligns them).

### 3. Verify ci-check.sh ≈ GitHub Actions

After both changes, verify the invariant: if ci-check.sh passes locally, GitHub
Actions will pass (barring environment differences like Python version, OS).

Document this invariant in ci-check.sh's header comment.

## Acceptance Criteria

- [ ] `scripts/**` in GitHub Actions paths filter (both push and pull_request)
- [ ] `.pre-commit-config.yaml` in paths filter
- [ ] `.github/workflows/**` in paths filter
- [ ] Ruff format check step in test-pytest job
- [ ] Ruff lint check step in test-pytest job
- [ ] Pattern lint step in test-pytest job (scoped to `adversarial_workflow/`)
- [ ] CI passes after changes (no regressions)
- [ ] ci-check.sh header documents the parity invariant

## Files to Modify

1. `.github/workflows/test-package.yml` — paths filter + new lint steps

## Error Handling for New Lint Steps

Ruff steps should **fail CI on error** — this is the safety net when pre-commit is
bypassed. Pattern lint is **advisory** (`continue-on-error: true`) until ADV-0061
cleans up the 34 existing DK002 violations.

- `ruff format --check .` exits non-zero on formatting issues → CI fails
- `ruff check .` exits non-zero on lint errors → CI fails
- `find ... | xargs python3 scripts/core/pattern_lint.py` → advisory (matches ci-check.sh)

## Testing Strategy

1. Create a branch with the workflow changes
2. Push a commit that touches `scripts/` only — verify CI triggers (it didn't before)
3. Verify all lint steps pass on current main
4. Verify ci-check.sh results match GitHub Actions results (the parity invariant)

## Notes

- This depends on ADV-0058 (ci-check.sh must be fixed first so we know what to mirror)
- Adding ruff to CI means formatting issues will block merges even if pre-commit
  was skipped — this is intentional
- Pattern lint in CI uses same scope as pre-commit (`adversarial_workflow/`)
- Performance: ruff + pattern_lint add ~5 seconds to CI. Negligible compared to
  the 6-matrix pytest runs (~3 min total)
- Consider whether `scripts/**` path changes should trigger only a subset of CI jobs
  (e.g., skip the full pytest matrix, just run lint + script syntax check) to save
  CI minutes. Not required for v1.
