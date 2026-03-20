# ADV-0035: Evaluator Runner Test Coverage - Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-19
**From**: Planner
**To**: feature-developer-v3
**Task**: delegation/tasks/2-todo/ADV-0035-evaluator-runner-test-coverage.md
**Status**: Ready for implementation
**Evaluation**: N/A (well-scoped testing task, no architectural risk)

---

## Task Summary

Increase test coverage for `adversarial_workflow/evaluators/runner.py` from 72% to 85%+. The module has 172 statements with 49 missing lines, mostly in error handling paths. There are currently 30 tests in 4 classes.

## Current Situation

The evaluator runner is the core execution engine — it shells out to `aider` to run evaluations. The happy paths are well-tested, but error handling (aider not found, subprocess failures, timeouts, output validation) has gaps. These are the paths that fail silently or with unhelpful errors in production.

## Your Mission

Write tests for the uncovered error paths in `runner.py`. This is a pure testing task — **do not modify `runner.py` itself** (unless a test reveals an actual bug).

### Phase 1: Read and Understand (15 min)
- Read `adversarial_workflow/evaluators/runner.py` (354 lines)
- Read existing `tests/test_evaluator_runner.py` (30 tests)
- Understand the mocking patterns already in use

### Phase 2: Write Tests (2-3h)
- Extend `tests/test_evaluator_runner.py` with new test classes/methods
- Target the specific missing lines listed below
- Follow existing test patterns and fixtures

### Phase 3: Verify (15 min)
- Run coverage: `.venv/bin/python -m pytest tests/test_evaluator_runner.py --cov=adversarial_workflow.evaluators.runner --cov-report=term-missing -q`
- Verify 85%+ achieved
- Run full suite: `.venv/bin/python -m pytest tests/ -q`

## Missing Lines to Cover

| Lines | Description | Priority | Suggested Test |
|-------|-------------|----------|----------------|
| 83-86, 90 | Aider binary not found | High | Mock `shutil.which` returning `None` |
| 102-114 | Subprocess errors (CalledProcessError, OSError) | High | Mock `subprocess.run` raising exceptions |
| 193-194 | Edge case in evaluator resolution | Low | Test with unusual evaluator config |
| 219-226 | Edge case in command building | Low | Test with edge-case parameters |
| 250-258, 268-269 | Output file validation failures | Medium | Test with empty/missing/corrupt output files |
| 312-315, 320-321 | Error reporting paths | Medium | Test with various error conditions |
| 334-339, 344, 349-354 | Timeout and cleanup | Medium | Mock subprocess timeout, verify cleanup |

## Key Mocking Patterns

The existing tests use `unittest.mock` (via `mocker` fixture from pytest-mock). Key things to mock:

```python
# Aider binary detection
mocker.patch('shutil.which', return_value=None)  # aider not found

# Subprocess execution
mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'aider'))
mocker.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('aider', 300))

# File system for output validation
# Use tmp_path fixture for creating test output files
```

## Defensive Coding Rules

- Check `.agent-context/patterns.yml` before writing code
- Use `==` for identifier comparison (DK002)
- Use `str.removesuffix()` for extension removal (DK003)
- Run `python3 scripts/core/pattern_lint.py` on any modified files

## Success Criteria

- `runner.py` coverage reaches **85%+** (currently 72%, need to cover ~22 more lines)
- All 500+ existing tests still pass
- New tests follow existing patterns and naming conventions
- No modifications to `runner.py` (tests only, unless bug found)

---

**Task File**: `delegation/tasks/2-todo/ADV-0035-evaluator-runner-test-coverage.md`
**Handoff Date**: 2026-03-19
**Coordinator**: Planner
