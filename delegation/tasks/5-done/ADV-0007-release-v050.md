# ADV-0007: Release v0.5.0 to PyPI

**Status**: Done
**Priority**: high
**Assigned To**: pypi-publisher
**Estimated Effort**: 30-45 minutes
**Created**: 2025-11-29
**Completed**: 2025-11-30

## Related Tasks

**Depends On**: ADV-0006 (Python 3.10 fix - complete)
**Blocks**: Users getting new features - NOW UNBLOCKED
**Related**: ADV-0003 (file splitting), ADV-0005 (Python version)

## Overview

Release version 0.5.0 to PyPI with new features and fixes since v0.4.0. Includes README updates to document new capabilities and correct Python version requirements.

**Context**: Significant changes since v0.4.0 warrant a new minor release:
- New `adversarial split` command (ADV-0003)
- Python 3.10+ requirement (ADV-0005)
- Python 3.10 compatibility fix (ADV-0006)

## Completion Summary

### Release Artifacts
- **PyPI**: https://pypi.org/project/adversarial-workflow/0.5.0/
- **GitHub Release**: v0.5.0: File Splitting & Python 3.10+
- **Git Tag**: v0.5.0

### What Was Done
1. Version updated to 0.5.0 in all locations (pyproject.toml, __init__.py, cli.py)
2. README updated with Python 3.10+ and `adversarial split` command
3. CHANGELOG.md updated with release notes
4. Package built and published to PyPI
5. GitHub release created with tag v0.5.0

## Acceptance Criteria

### Must Have
- [x] Version 0.5.0 in pyproject.toml, __init__.py, cli.py
- [x] README updated with Python 3.10+ and split command
- [x] CHANGELOG.md updated with release notes
- [x] Package published to PyPI
- [x] `pip install adversarial-workflow` gets v0.5.0

### Should Have
- [x] GitHub release created with tag v0.5.0
- [x] Release notes document breaking changes

## Pre-Release Checklist

- [x] All CI/CD tests passing
- [x] Version numbers consistent
- [x] README accurate
- [x] CHANGELOG complete
- [x] No uncommitted changes

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Update README | 10 min | [x] |
| Update versions | 5 min | [x] |
| Update CHANGELOG | 10 min | [x] |
| Build & publish | 10 min | [x] |
| GitHub release | 5 min | [x] |
| Verify | 5 min | [x] |
| **Total** | **45 min** | [x] |

## References

- **PyPI**: https://pypi.org/project/adversarial-workflow/0.5.0/
- **GitHub Release**: https://github.com/movito/adversarial-workflow/releases/tag/v0.5.0
- **Previous version**: 0.4.0
- **Released version**: 0.5.0

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-30
