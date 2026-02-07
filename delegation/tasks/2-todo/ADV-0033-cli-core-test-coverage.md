# ADV-0033: CLI Core Commands Test Coverage

**Status**: Todo
**Priority**: Medium
**Created**: 2026-02-07
**Type**: Testing
**Estimated Effort**: 4-6 hours

---

## Problem Statement

`cli.py` has 37% test coverage (1693 statements, 1062 uncovered). This is the largest coverage gap in the codebase. The CLI is the primary user interface and should have comprehensive testing.

## Scope

**Phase 1 - Core Commands** (this task):
- `evaluate` command
- `init` command
- `check` command
- `split` command
- Basic argument parsing and validation

**Out of scope** (separate task ADV-0034):
- Library commands (`library install`, `library list`, etc.)
- Agent commands (`agent onboard`, etc.)

## Current State

```
adversarial_workflow/cli.py    1693   1062    37%
```

**Target**: Increase cli.py coverage to 50%+ (Phase 1)

## Acceptance Criteria

- [ ] `evaluate` command has tests for:
  - [ ] Basic file evaluation
  - [ ] `--evaluator` flag
  - [ ] `--dry-run` flag
  - [ ] Error handling (missing file, invalid evaluator)
- [ ] `init` command has tests for:
  - [ ] Fresh initialization
  - [ ] Re-initialization (existing config)
  - [ ] `--force` flag
- [ ] `check` command has tests for:
  - [ ] Valid configuration
  - [ ] Invalid/missing configuration
- [ ] `split` command has tests for:
  - [ ] Basic splitting
  - [ ] Custom chunk size
  - [ ] Error handling
- [ ] CLI argument parsing validated
- [ ] Overall cli.py coverage reaches 50%+

## Implementation Notes

### Test Structure

```python
# tests/test_cli_core.py

class TestEvaluateCommand:
    def test_evaluate_basic(self, tmp_path, cli_runner):
        ...
    def test_evaluate_with_evaluator_flag(self, ...):
        ...
    def test_evaluate_dry_run(self, ...):
        ...

class TestInitCommand:
    def test_init_fresh(self, ...):
        ...
    def test_init_existing_warns(self, ...):
        ...

class TestCheckCommand:
    ...

class TestSplitCommand:
    ...
```

### Testing Approach

1. Use Click's `CliRunner` for command testing
2. Mock external dependencies (aider, file system where needed)
3. Use `tmp_path` fixture for file operations
4. Test both success and error paths

### Key Areas in cli.py

| Lines | Function | Priority |
|-------|----------|----------|
| 60-201 | `evaluate` command | High |
| 208-356 | `init` command | High |
| 363-503 | `check` command | Medium |
| 508-590 | `split` command | Medium |

## Related

- ADV-0034: CLI Library Commands Test Coverage (Phase 2)
- ADV-0035: Evaluator Runner Test Coverage

---

**Notes**: Focus on user-facing behavior, not implementation details. Mock aider/external calls to keep tests fast and deterministic.
