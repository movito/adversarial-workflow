# ADV-0006: Fix Python 3.10 Compatibility (tomllib)

**Status**: Todo
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 15-30 minutes
**Created**: 2025-11-29

## Related Tasks

**Depends On**: None
**Blocks**: CI/CD 100% pass rate
**Related**: ADV-0005 (Python version compatibility)

## Overview

Fix Python 3.10 test failure caused by using `tomllib` module which is only available in Python 3.11+. The project declares `requires-python = ">=3.10"` but tests fail on Python 3.10.

**Context**: CI/CD pipeline shows Python 3.10 tests failing with import error. Python 3.11 and 3.12 pass. This was introduced when `test_python_version.py` was added.

## Requirements

### Functional Requirements
1. Tests must pass on Python 3.10
2. Use `tomli` package as fallback for Python < 3.11
3. Add `tomli` to dev dependencies with version constraint

### Non-Functional Requirements
- [ ] Backward compatible with Python 3.10
- [ ] No changes needed for Python 3.11+
- [ ] CI/CD passes on all Python versions

## TDD Workflow (Mandatory)

**Fix-Driven Approach**:

1. **Identify**: Locate the failing import
2. **Fix**: Add conditional import with fallback
3. **Test**: Verify locally on Python 3.10 (if available) or via CI
4. **Verify**: Push and confirm CI passes

## Implementation Plan

### Files to Modify

1. `tests/test_python_version.py`
   - Line: `import tomllib`
   - Change: Add try/except fallback to `tomli`

2. `pyproject.toml`
   - Section: `[project.optional-dependencies]`
   - Change: Add `tomli` for Python < 3.11

### Fix

**Step 1: Update test file**

```python
# tests/test_python_version.py
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
```

**Step 2: Update pyproject.toml**

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
    "black>=22.0",
    "isort>=5.0",
    "flake8>=4.0",
    "tomli>=2.0; python_version < '3.11'",
]
```

### Optional: Remove ubuntu-20.04 from CI matrix

The CI also shows ubuntu-20.04 jobs stuck in queue. Consider removing from `.github/workflows/test-package.yml`:

```yaml
# Change from:
os: [ubuntu-22.04, ubuntu-20.04, macos-latest]

# To:
os: [ubuntu-22.04, macos-latest]
```

## Acceptance Criteria

### Must Have
- [ ] Python 3.10 tests pass
- [ ] Python 3.11 tests still pass
- [ ] Python 3.12 tests still pass
- [ ] CI/CD all green

### Should Have
- [ ] ubuntu-20.04 issue addressed (remove or fix)

## Success Metrics

### Quantitative
- CI/CD pass rate: 100%
- All Python versions: 3.10, 3.11, 3.12 passing

### Qualitative
- No import errors on any supported Python version

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Fix test import | 5 min | [ ] |
| Update pyproject.toml | 5 min | [ ] |
| Fix CI matrix (optional) | 5 min | [ ] |
| Push and verify | 10 min | [ ] |
| **Total** | **25 min** | [ ] |

## References

- **Failing test**: `tests/test_python_version.py`
- **CI Run**: https://github.com/movito/adversarial-workflow/actions/runs/19790339526
- **tomllib docs**: https://docs.python.org/3/library/tomllib.html (3.11+)
- **tomli package**: https://pypi.org/project/tomli/

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-29
