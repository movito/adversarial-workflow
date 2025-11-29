# ADV-0005: Fix Python Version Compatibility

**Status**: Todo
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 30 minutes
**Created**: 2025-11-29

## Related Tasks

**Depends On**: None
**Blocks**: CI/CD pipeline full success
**Related**: ADV-0004-E5 (CI/CD pipeline revealed this issue)

## Overview

Update Python version requirements from `>=3.8` to `>=3.10` across the project. The `aider-chat` dependency doesn't support Python 3.8/3.9, causing CI/CD failures.

**Context**: CI/CD pipeline (ADV-0004-E5) revealed that all Python 3.8 and 3.9 jobs fail during package installation. The `aider-chat>=0.86.0` dependency requires Python 3.10+.

## Requirements

### Functional Requirements
1. Update `pyproject.toml` to require Python >=3.10
2. Update CI/CD matrix to remove Python 3.8/3.9
3. Update documentation to reflect supported versions

### Non-Functional Requirements
- [ ] Accuracy: All version references consistent
- [ ] CI/CD: All jobs pass after change
- [ ] Documentation: README reflects correct versions

## TDD Workflow (Mandatory)

**Verification-Driven Approach** (config change):

1. **Verify**: Check current CI/CD failure pattern
2. **Update**: Change version requirements
3. **Test**: Push and verify CI/CD passes
4. **Document**: Update any version references

### Verification Requirements
- [ ] CI/CD passes for Python 3.10, 3.11, 3.12
- [ ] No references to Python 3.8/3.9 remain
- [ ] Package installs correctly with new requirements

## Implementation Plan

### Files to Modify

1. `pyproject.toml`
   - Line: `requires-python = ">=3.8"` → `">=3.10"`
   - Section: `classifiers` - remove 3.8, 3.9 entries

2. `.github/workflows/test-package.yml`
   - Remove `'3.8'` and `'3.9'` from Python version matrix

3. `README.md` (if version mentioned)
   - Update any Python version references

### Approach

**Step 1: Update pyproject.toml**

```toml
# Change from:
requires-python = ">=3.8"

# To:
requires-python = ">=3.10"

# Remove classifiers:
"Programming Language :: Python :: 3.8",
"Programming Language :: Python :: 3.9",
```

**Step 2: Update CI/CD Matrix**

```yaml
# Change from:
python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

# To:
python-version: ['3.10', '3.11', '3.12']
```

**Step 3: Verify**

Push changes and confirm all CI/CD jobs pass.

## Acceptance Criteria

### Must Have
- [ ] `pyproject.toml` requires Python >=3.10
- [ ] CI/CD matrix only includes 3.10, 3.11, 3.12
- [ ] All CI/CD jobs pass
- [ ] Package installs on Python 3.10+

### Should Have
- [ ] Classifiers updated in pyproject.toml
- [ ] README updated if needed

## Success Metrics

### Quantitative
- CI/CD pass rate: 100% (currently 52% due to 3.8/3.9 failures)
- All 16 remaining jobs pass (was 21 with 3.8/3.9)

### Qualitative
- Version requirements match actual dependency support
- No misleading compatibility claims

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Update pyproject.toml | 5 min | [ ] |
| Update CI/CD workflow | 5 min | [ ] |
| Push and verify | 15 min | [ ] |
| Update docs if needed | 5 min | [ ] |
| **Total** | **30 min** | [ ] |

## References

- **CI/CD Run**: https://github.com/movito/adversarial-workflow/actions/runs/19788734291
- **aider-chat**: Requires Python 3.10+ (verified)
- **Failing jobs**: Python 3.8, 3.9 on Ubuntu and macOS

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-29
