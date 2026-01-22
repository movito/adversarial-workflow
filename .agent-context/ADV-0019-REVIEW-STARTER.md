# Review Starter: ADV-0019 - List Evaluators Command and Documentation

**Task ID**: ADV-0019
**Implemented By**: feature-developer
**Date**: 2025-01-23
**PR**: https://github.com/movito/adversarial-workflow/pull/11
**Branch**: `feature/adv-0019-list-evaluators-docs`

## Implementation Summary

Added the `adversarial list-evaluators` command to display all available evaluators (built-in and local) and comprehensive documentation for the plugin architecture. This is the final task in the v0.6.0 plugin implementation chain.

### What Was Implemented

1. **CLI Command**: `list_evaluators()` function in `cli.py`
   - Shows built-in evaluators with descriptions
   - Shows local evaluators with aliases, model, and version
   - Deduplicates aliases (only shows primary evaluator entry)
   - Helpful message when no local evaluators exist

2. **CLI Registration**:
   - Added `list-evaluators` to `STATIC_COMMANDS` to prevent override
   - Registered subparser for the command
   - Added command dispatch handler

3. **Test Suite**: 6 comprehensive tests in `tests/test_list_evaluators.py`

4. **Documentation**:
   - README.md: Custom Evaluators section (~70 lines)
   - docs/CUSTOM_EVALUATORS.md: Full guide (~300 lines)
   - docs/examples/athena.yml: Example evaluator
   - CHANGELOG.md: v0.6.0 release notes

## Files Changed

| File | Change Type | Lines |
|------|-------------|-------|
| `adversarial_workflow/cli.py` | Modified | +45 |
| `tests/test_list_evaluators.py` | Created | +110 |
| `README.md` | Modified | +70 |
| `docs/CUSTOM_EVALUATORS.md` | Created | ~300 |
| `docs/examples/athena.yml` | Created | ~100 |
| `CHANGELOG.md` | Modified | +24 |

**Total**: ~650 lines added

## Test Results

```
============================= 166 passed in 3.04s ==============================
```

All existing tests pass. 6 new tests added for list-evaluators functionality.

## Automated Review Feedback

### CodeRabbit
- **Fixed**: Unused loop variable `name` → changed to `_` (commit d8c8b15)
- **Trivial/Optional**: Markdown formatting (blank lines around code blocks) - not blocking

### BugBot
- **By Design**: `review` shown in built-in evaluators but works as static command (no file argument). This is intentional - `review` reviews git diffs, not individual files.

## Areas to Focus On

1. **CLI Implementation** (`adversarial_workflow/cli.py:2827-2866`)
   - Verify `list_evaluators()` function correctness
   - Check STATIC_COMMANDS protection works
   - Verify output formatting

2. **Test Coverage** (`tests/test_list_evaluators.py`)
   - Tests cover: builtins, no local, with local, help output, alias dedup, version display
   - Verify tests are meaningful and not brittle

3. **Documentation Accuracy**
   - README custom evaluators section matches actual behavior
   - CUSTOM_EVALUATORS.md schema matches EvaluatorConfig dataclass
   - Example athena.yml is valid YAML

4. **Acceptance Criteria** (from task file):
   - [ ] `adversarial list-evaluators` shows built-in evaluators
   - [ ] `adversarial list-evaluators` shows local evaluators with details
   - [ ] Helpful message when no local evaluators exist
   - [ ] README.md updated with Custom Evaluators section
   - [ ] docs/CUSTOM_EVALUATORS.md created with full documentation
   - [ ] docs/examples/athena.yml created as reference
   - [ ] CHANGELOG.md updated for v0.6.0
   - [ ] Unit tests for list-evaluators command
   - [ ] All existing tests pass

## Dependencies

This task depends on:
- ADV-0015: EvaluatorConfig dataclass
- ADV-0016: Evaluator discovery (`discover_local_evaluators`)
- ADV-0017: Generic evaluator runner
- ADV-0018: Dynamic CLI registration

All dependencies are merged into main.

## Quick Verification Commands

```bash
# Run list-evaluators command
adversarial list-evaluators

# Run specific tests
source .venv/bin/activate && pytest tests/test_list_evaluators.py -v

# Check command appears in help
adversarial --help | grep list-evaluators

# Verify PR status
gh pr view 11 --comments
gh pr checks 11
```

## Task File Location

`delegation/tasks/2-todo/ADV-0019-list-evaluators-and-docs.md`

(Note: Task should be moved to `4-in-review/` for formal review)
