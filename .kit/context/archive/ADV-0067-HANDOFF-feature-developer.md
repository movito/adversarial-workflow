# ADV-0067: Fix Pre-Existing CLI Issues — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-04-13
**From**: Planner
**To**: feature-developer-v5
**Task**: `delegation/tasks/2-todo/ADV-0067-fix-cli-preexisting-issues.md`
**Status**: Ready for implementation
**Evaluation**: Skipped (mechanical refactor, low evaluator signal per ADV-0065/0066 retros)

---

## Task Summary

Fix 3 pre-existing issues in `cli.py` found during ADV-0066:
1. Remove ~55 lines of dead verdict-extraction code from `evaluate()`
2. Add empty `test_command` guard in `validate()`
3. Clean up orphaned imports

## The Core Fix

`cli.evaluate()` calls `run_evaluator()`, which already:
- Calls the LLM
- Writes the log file
- Parses the verdict
- Prints the verdict
- Returns 0 (pass) or 1 (revision/rejected)

Then `evaluate()` re-opens the log file, re-parses the verdict, and has its own NEEDS_REVISION/REJECTED branches — but those branches are unreachable because `run_evaluator()` already returned 1 for those verdicts (and `evaluate()` exited at line 1728-1732).

**Fix**: Delete lines 1734-1794 and replace with the same pattern `review()` already uses (lines 1861-1869).

## Files to Change

1. `adversarial_workflow/cli.py` — Simplify `evaluate()`, guard `validate()`
2. `tests/test_cli_core.py` — Update evaluate tests, add validate edge cases
3. `tests/test_evaluate.py` — Update any tests that check for verdict re-parsing

## Critical Details

### What `review()` looks like (the target pattern):
```python
eval_result = run_evaluator(builtin_config, task_file)
if eval_result != 0:
    print()
    print("📋 Review complete (needs revision)")
    return eval_result

print()
print(f"{GREEN}✅ Review approved!{RESET}")
return 0
```

### What to delete from `evaluate()`:
- Lines 1734-1794: log file search via glob, `validate_evaluation_output()` call, all verdict branches
- The `import glob` statement (if only used here)
- The `verify_token_count()` call (check if used elsewhere first)

### validate() guard to add (before `shlex.split`):
```python
if not test_command or not test_command.strip():
    print(f"{RED}❌ ERROR: Test command is empty{RESET}")
    print("   Fix: Provide a test command or set test_command in .adversarial/config.yml")
    return 1
```

## Starting Point

1. `git checkout -b feature/ADV-0067-fix-cli-preexisting-issues`
2. `./scripts/core/project start ADV-0067`
3. Read `adversarial_workflow/cli.py` lines 1697-1914
4. Write failing tests for simplified evaluate() + validate("") guard
5. Implement

---

**Task File**: `delegation/tasks/2-todo/ADV-0067-fix-cli-preexisting-issues.md`
**Handoff Date**: 2026-04-13
**Coordinator**: Planner
