# Review Starter: ADV-0031

**Task**: ADV-0031 - Library Evaluator Execution
**Task File**: `delegation/tasks/4-in-review/ADV-0031-library-evaluator-execution.md`
**Branch**: feat/adv-0031-evaluator-execution → main
**PR**: Not yet created (feature branch pushed)

## Implementation Summary

- Added `--evaluator`/`-e` flag to the `evaluate` CLI command
- When flag specified, looks up evaluator by name or alias from `.adversarial/evaluators/`
- Reuses existing `run_evaluator()` function for model resolution and execution
- Backward compatible: without flag, uses existing built-in evaluate behavior
- Proper error messages when evaluator not found (lists available evaluators with aliases)

## Files Changed

- `adversarial_workflow/cli.py` (modified) - Added flag and handler logic
- `tests/test_evaluate_with_evaluator.py` (new) - 9 tests covering:
  - Flag appears in help
  - Other evaluators don't have flag
  - Error when no evaluators installed
  - Error shows available evaluators
  - Selection by name
  - Selection by alias
  - Short flag (-e) works
  - Backward compatibility
  - Aliases displayed in error messages

## Test Results

- 388 tests passing (including 9 new tests)
- 58% coverage overall
- CI passed on GitHub (all 12 jobs: Python 3.10/3.11/3.12 on Ubuntu and macOS)

## Areas for Review Focus

1. **Error handling completeness** - Are all edge cases covered?
2. **Timeout precedence** - Uses `config_to_use.timeout` instead of `args.evaluator_config.timeout`
3. **Alias resolution** - Uses existing `discover_local_evaluators()` which returns both names and aliases
4. **No new function created** - Reused `run_evaluator()` instead of creating `run_with_evaluator()`

## Design Decisions

1. **Flag only on "evaluate" command** - Not added to other evaluators (proofread, etc.) to keep scope minimal
2. **Reuse run_evaluator()** - The existing function already handles model resolution, API key checks, and execution - no need to duplicate
3. **Discovery at runtime** - Uses `discover_local_evaluators()` when flag is provided, not at CLI startup

## Related ADRs

- None directly applicable

---
**Ready for code-reviewer agent in new tab**
