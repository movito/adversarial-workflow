# ADV-0001: Test Infrastructure Setup

**Status**: Todo
**Priority**: high
**Estimate**: 2-3 hours

## Overview

Set up comprehensive test infrastructure for adversarial-workflow. The current codebase has no tests, and cli.py is a 2800+ line monolith that needs test coverage before refactoring.

## Background

- `adversarial_workflow/cli.py` contains all functionality
- No existing test coverage
- Pre-commit hooks are configured but need tests to run
- TDD workflow requires tests-first approach

## Requirements

### Must Have
- [ ] Pytest configured with proper paths
- [ ] Basic smoke tests for CLI commands
- [ ] Test fixtures for common test data
- [ ] Coverage reporting enabled

### Should Have
- [ ] Tests for `evaluate` command (mock aider)
- [ ] Tests for config loading
- [ ] Tests for file path handling

### Nice to Have
- [ ] Integration tests with real aider (marked slow)
- [ ] Coverage threshold enforcement

## Technical Details

### Test Structure
```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_cli.py          # CLI smoke tests
├── test_config.py       # Config loading tests
├── test_evaluate.py     # Evaluate command tests
└── fixtures/
    └── sample_task.md   # Test task file
```

### Key Functions to Test (cli.py)
1. `main()` - Entry point
2. `cmd_evaluate()` - Evaluate command
3. `load_config()` - Config loading
4. `find_aider()` - Aider discovery
5. `run_evaluation()` - Core evaluation logic

### Mocking Strategy
- Mock `subprocess.run` for aider calls
- Mock file I/O for config loading
- Use tmp_path fixture for file tests

## Acceptance Criteria

1. `pytest tests/ -v` runs successfully
2. All smoke tests pass
3. Coverage report shows tested functions
4. Pre-commit hook runs tests on commit

## References

- conftest.py already exists at project root
- .pre-commit-config.yaml has pytest-fast hook
- pyproject.toml has pytest configuration
