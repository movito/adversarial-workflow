# ADV-0009: Additional Platform Testing

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours per platform
**Created**: 2025-11-30

## Related Tasks

**Depends On**: None
**Blocks**: None
**Related**: ADV-0004 (parent meta-task), ADV-0001 (test infrastructure)
**Split From**: ADV-0004-E2

## Overview

Extend platform testing coverage beyond current CI/CD matrix (macOS Intel, Ubuntu 22.04, Python 3.10-3.12) to verify compatibility on additional platforms requested by users.

**Context**: Current CI/CD tests on Linux and macOS Intel. Users may run on WSL, macOS ARM (M1/M2/M3), Alpine, CentOS/RHEL, or FreeBSD. Testing ensures compatibility and documents any platform-specific issues.

## Requirements

### Functional Requirements
1. Test on additional platforms as needed
2. Document platform-specific issues or workarounds
3. Add platform-specific tests if needed
4. Update CI/CD matrix for supported platforms

### Non-Functional Requirements
- [ ] Test results documented
- [ ] Known issues listed in TROUBLESHOOTING.md
- [ ] CI/CD updated if platform is to be officially supported

## Candidate Platforms

| Platform | Priority | Effort | Trigger |
|----------|----------|--------|---------|
| macOS ARM (M1/M2/M3) | High | 2 hrs | User reports |
| WSL (Windows Subsystem) | High | 2 hrs | Windows user issues |
| Alpine Linux | Medium | 2 hrs | Docker users |
| CentOS/RHEL | Medium | 3 hrs | Enterprise users |
| FreeBSD | Low | 4 hrs | Niche use case |

## TDD Workflow (Mandatory)

### Red Phase
1. Run existing test suite on target platform
2. Document any failures
3. Create platform-specific test cases if needed

### Green Phase
1. Fix platform-specific issues
2. Add workarounds or dependencies
3. Verify all tests pass

### Refactor Phase
1. Update documentation
2. Add to CI/CD if warranted
3. Create platform-specific install notes

## Implementation Plan

### Step 1: macOS ARM Testing (if triggered)

```bash
# On M1/M2/M3 Mac
pip install adversarial-workflow
pytest tests/ -v
adversarial --version
adversarial init test-project
```

### Step 2: WSL Testing (if triggered)

```bash
# In WSL2
pip install adversarial-workflow
pytest tests/ -v
# Test path handling between Windows/Linux
```

### Step 3: Docker/Alpine Testing

```dockerfile
FROM python:3.12-alpine
RUN pip install adversarial-workflow
RUN adversarial --version
```

## Acceptance Criteria

### Must Have (per platform)
- [ ] All existing tests pass
- [ ] Core commands work (init, evaluate, split)
- [ ] Issues documented if any

### Should Have
- [ ] CI/CD integration for high-priority platforms
- [ ] Platform notes in installation docs

## Time Estimate

| Platform | Time | Status |
|----------|------|--------|
| macOS ARM | 2 hrs | [ ] |
| WSL | 2 hrs | [ ] |
| Alpine | 2 hrs | [ ] |
| CentOS/RHEL | 3 hrs | [ ] |
| FreeBSD | 4 hrs | [ ] |

## References

- **Current CI/CD**: `.github/workflows/ci.yml`
- **Supported platforms**: macOS (Intel), Ubuntu 22.04
- **Python versions**: 3.10, 3.11, 3.12

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-30
