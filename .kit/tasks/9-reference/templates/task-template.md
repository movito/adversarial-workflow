# ADV-NNNN: [Task Title]

**Status**: [Choose ONE: Backlog | Todo | In Progress | In Review | Done | Canceled | Blocked]
**Priority**: critical | high | medium | low
**Assigned To**: [agent-name or unassigned]
**Estimated Effort**: X-Y hours
**Created**: YYYY-MM-DD

## Related Tasks

**Depends On**: ADV-NNNN [tasks that must complete before this one]
**Blocks**: ADV-NNNN [tasks that cannot start until this completes]

## Overview

[1-2 paragraph description of the task. What needs to be done and why it matters.]

**Context**: [Background information, related work, or upstream dependencies]

## Requirements

### Functional Requirements
1. [Requirement 1 - specific, measurable]
2. [Requirement 2 - specific, measurable]
3. [Requirement 3 - specific, measurable]

### Non-Functional Requirements
- [ ] Performance: [Specific targets]
- [ ] Reliability: [Specific targets]
- [ ] Maintainability: [Code quality standards]

## TDD Workflow (Mandatory)

**Test-Driven Development Approach**:

1. **Red**: Write failing tests for feature
2. **Green**: Implement minimum code until tests pass
3. **Refactor**: Improve code while keeping tests green
4. **Commit**: Pre-commit hook runs tests automatically

### Test Requirements
- [ ] Unit tests for all new functions/classes
- [ ] Error handling tests for edge cases
- [ ] Coverage: 80%+ for new code

**Test files to create**:
- `tests/test_<feature>.py` - Main test suite

## Implementation Plan

### Files to Modify

1. `adversarial_workflow/<file>.py` - [Description]
   - Function/class: `function_name()`
   - Change: [What will be modified]

### Files to Create

1. `tests/test_<feature>.py` - Test suite
   - Purpose: Test coverage for new functionality

### Approach

**Step 1: [Phase Name]**

[Description of what happens in this step]

**TDD cycle**:
1. Write tests: [Specific tests to write]
2. Run tests (should fail): `pytest tests/test_<feature>.py -v`
3. Implement feature: [What to implement]
4. Run tests (should pass): `pytest tests/test_<feature>.py -v`

## Acceptance Criteria

### Must Have
- [ ] All functional requirements implemented
- [ ] All tests passing
- [ ] Coverage targets met (80%+ new code)
- [ ] No regressions in existing tests

### Should Have
- [ ] Error messages are clear and actionable
- [ ] Code is well-commented

## Success Metrics

### Quantitative
- Test pass rate: 100%
- Coverage increase: [Target]

### Qualitative
- Code review feedback: Clean
- Maintainability: Improved

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Write failing tests | X hours | [ ] |
| Implement features | X hours | [ ] |
| Refactor & optimize | X hours | [ ] |
| **Total** | **X hours** | [ ] |

## References

- **Testing**: `pytest tests/ -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow`
- **Pre-commit**: `pre-commit run --all-files`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2025-11-28
