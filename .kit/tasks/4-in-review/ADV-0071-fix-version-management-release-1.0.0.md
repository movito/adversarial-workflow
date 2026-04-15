# ADV-0071: Fix Version Management + Release 0.9.11

**Status**: In Review
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-04-14

## Related Tasks

**Depends On**: None
**Blocks**: 1.0.0 release
**Related**: ADV-0065 through ADV-0070 (structural cleanup series that qualifies us for 1.0.0)

## Overview

The version management in `adversarial_workflow` has a long-standing bug: hardcoded fallback
version strings in `cli.py` and `__init__.py` drift from the canonical version in `pyproject.toml`.
This causes the `test_version_flag` test to fail in certain subprocess environments (e.g., when
`ci-check.sh` invokes pytest, the `adversarial --version` subprocess picks up the stale fallback).

This task fixes the single-source-of-truth version problem, then bumps to 1.0.0.

## Problem Analysis

### Current State (broken)

```python
# adversarial_workflow/__init__.py (line 15-20)
try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version("adversarial-workflow")
except Exception:
    __version__ = "0.9.9"  # ← STALE, should be 0.9.10

# adversarial_workflow/cli.py (line 31-36) — identical pattern
try:
    from importlib.metadata import version as _get_version
    __version__ = _get_version("adversarial-workflow")
except Exception:
    __version__ = "0.9.9"  # ← STALE, should be 0.9.10
```

### Why It Fails

1. `importlib.metadata.version()` reads from the **installed** package metadata
2. When `ci-check.sh` runs `pytest`, it spawns `adversarial --version` as a subprocess
3. The subprocess may use a different Python or a stale editable install
4. When metadata lookup fails, it falls back to the hardcoded `"0.9.9"`
5. The test compares `version("adversarial-workflow")` (from in-process metadata = 0.9.10)
   against `result.stdout` (from subprocess = `"0.9.9"`) → mismatch → FAIL

### Root Cause

Two hardcoded version strings that must be updated manually every release. This has been
a known issue since at least v0.9.5 (see CHANGELOG entry about `__version__` using
`importlib.metadata.version()` as single source of truth — but the fallback was never removed).

## Requirements

### Fix Version Management

1. **Eliminate hardcoded fallback versions** from both `__init__.py` and `cli.py`
2. **Single source of truth**: `pyproject.toml` → `importlib.metadata` → `__version__`
3. Since we require Python 3.10+, `importlib.metadata` is always available
4. If the package isn't installed, `_get_version()` raises `PackageNotFoundError` — this
   should propagate (not be silently swallowed), since an uninstalled package can't run anyway

### Approach Options

**Option A: Remove try/except entirely**
```python
from importlib.metadata import version as _get_version
__version__ = _get_version("adversarial-workflow")
```
Simple, clean. Fails loudly if package isn't installed. Correct for a pip-installed CLI tool.

**Option B: Read from pyproject.toml at import time**
```python
# Read version from pyproject.toml directly
import tomllib
with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
    __version__ = tomllib.load(f)["project"]["version"]
```
Works without install, but fragile (path assumptions, file I/O at import time).

**Option C: Build-time version injection**
Use setuptools-scm or similar to inject version at build time. Overkill for this project.

**Recommendation**: Option A. It's what `importlib.metadata` was designed for, and it's
what our code already tries to do — the fallback just masks failures.

### Fix the Test

The `test_version_flag` test in `tests/test_cli.py` should be robust:
- It compares in-process `version("adversarial-workflow")` with subprocess `adversarial --version`
- After fixing the source, both should always agree
- Consider whether the test should also verify the version matches `pyproject.toml` directly

### Bump to 1.0.0

After version management is fixed:

1. Bump `pyproject.toml` version to `1.0.0`
2. Write CHANGELOG `[1.0.0]` section (content drafted below)
3. Add version footer to README.md
4. Verify all tests pass (including `test_version_flag`)
5. Verify `ci-check.sh` passes fully

### CHANGELOG Content for 1.0.0

```markdown
## [1.0.0] - 2026-04-14

### Changed
- **`.kit/` directory migration** — builder infrastructure moved into `.kit/` hierarchy (ADV-0068)
- **Root declutter** — root reduced from 15 to 9 files; manifest upgraded to v2.0.0 (ADV-0069)
- **docs/ consolidation** — 9 subdirectories → 4: adr/, archive/, guides/, reference/ (ADV-0070)
- **Agent definitions** — updated to latest models with standardized frontmatter metadata
- **Monitoring sub-agent** — now runs in worktree isolation with no-commit guardrail
- **Version management** — removed hardcoded fallback versions; single source of truth via pyproject.toml

### Removed
- 7 obsolete agent definitions (v1, v3, v4, sonnet-v3, planner, test-runner, ci-checker)
- `docs/decisions/` nesting layer — ADRs now at `docs/adr/` directly
- Historical docs directories consolidated into `docs/archive/`

### Fixed
- **Launcher scripts** — PROJECT_ROOT resolution fixed after .kit/ migration
- **Bot-watcher agent reference** — replaced non-existent agent type with general-purpose
- **Version fallback** — removed stale hardcoded version strings that caused test failures
```

## Implementation Plan

### Phase 1: Fix version management (30 min)

1. Remove try/except fallback from `adversarial_workflow/__init__.py`
2. Remove try/except fallback from `adversarial_workflow/cli.py`
3. Ensure `__init__.py` imports `__version__` from a single location (DRY)
4. Run `pytest tests/test_cli.py -v` to verify

### Phase 2: Verify CI compatibility (30 min)

1. Run `./scripts/core/ci-check.sh` — must pass fully
2. If subprocess still picks up stale version, investigate the `run_cli` fixture
3. May need to ensure `pip install -e .` is part of CI setup

### Phase 3: Bump to 1.0.0 (30 min)

1. Update `pyproject.toml` version
2. Write CHANGELOG section
3. Add README version footer
4. Reinstall: `pip install -e ".[dev]"`

### Phase 4: Verify + Ship (30 min)

1. `pytest tests/ -v` — all pass
2. `./scripts/core/ci-check.sh` — all pass
3. `pre-commit run --all-files` — all pass
4. Commit, push, open PR
5. After merge: `git tag -a v1.0.0 -m "Release v1.0.0"` + push tag

## TDD Workflow

### Test Requirements
- [ ] `test_version_flag` passes in direct pytest AND in ci-check.sh
- [ ] No hardcoded version strings remain (grep for `"0.9.`)
- [ ] `adversarial --version` reports 1.0.0
- [ ] All 530 existing tests pass
- [ ] Coverage: N/A (minimal code change)

## Acceptance Criteria

### Must Have
- [ ] No hardcoded version fallback in `__init__.py` or `cli.py`
- [ ] `pyproject.toml` is the single source of truth for version
- [ ] `test_version_flag` passes in `ci-check.sh` (not just standalone pytest)
- [ ] Version bumped to 1.0.0
- [ ] CHANGELOG written for 1.0.0
- [ ] README has version footer
- [ ] All tests pass
- [ ] CI passes on GitHub

### Should Have
- [ ] No duplicate `__version__` definitions (DRY — define once, import elsewhere)
- [ ] Git tag v1.0.0 created after merge

## Success Metrics

### Quantitative
- Hardcoded version strings: 2 → 0
- Test failures in ci-check.sh: 1 → 0

### Qualitative
- Version bumps now require editing only `pyproject.toml`
- No more version drift between releases

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Fix version management | 30 min | [ ] |
| Verify CI compatibility | 30 min | [ ] |
| Bump to 1.0.0 | 30 min | [ ] |
| Verify + ship | 30 min | [ ] |
| Bot review rounds | 30 min | [ ] |
| **Total** | **~2.5 hours** | [ ] |

## References

- **pyproject.toml**: Single source of truth for version
- **cli.py lines 31-36**: Current fallback
- **__init__.py lines 15-20**: Current fallback
- **tests/test_cli.py line 17**: `test_version_flag`
- **tests/conftest.py line 189**: `run_cli` fixture
- **CHANGELOG.md**: Release notes
- **ci-check.sh line 91**: Where pytest is invoked

## Review

**PR**: #67
**Branch**: feature/ADV-0071-fix-version-management -> main

### Artifacts
- Review starter: `.kit/context/ADV-0071-REVIEW-STARTER.md`
- Evaluator review: `.kit/context/reviews/ADV-0071-evaluator-review.md`

### Files Changed
- `adversarial_workflow/__init__.py` (modified)
- `adversarial_workflow/cli.py` (modified)
- `pyproject.toml` (modified)
- `tests/conftest.py` (modified)
- `CHANGELOG.md` (modified)
- `README.md` (modified)

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-15
