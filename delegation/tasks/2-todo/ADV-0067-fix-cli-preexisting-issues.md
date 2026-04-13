# ADV-0067: Fix Pre-Existing CLI Issues (Evaluate/Review/Validate)

**Status**: Todo
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-04-13
**Depends On**: ADV-0066 (merged PR #61)

## Related Tasks

**Depends On**: ADV-0066 (Remove aider remnants — DONE)
**Blocks**: v1.0.0 release (clean up known issues before release)
**Source**: `.agent-context/ADV-0066-preexisting-issues.md`

## Overview

Four pre-existing issues were identified during ADV-0066. Issues #1 and #4 are the same root cause (duplicate verdict extraction), #2 is a defensive guard, and #3 is theoretical (no action needed). This task fixes the three actionable items.

**Context**: `run_evaluator()` already handles verdict extraction, reporting, and exit codes. But `cli.evaluate()` duplicates this work — it calls `run_evaluator()`, then re-opens the log file, re-parses the verdict, and has its own verdict-handling branches. The NEEDS_REVISION and REJECTED branches in `cli.evaluate()` are dead code because `run_evaluator()` already returned 1 for those verdicts (and `cli.evaluate()` exited at line 1728-1732).

## Requirements

### Functional Requirements

1. **Remove duplicate verdict extraction in `cli.evaluate()`** (lines 1734-1794)
   - After `run_evaluator()` returns 0, the verdict was already APPROVED (or unknown-treated-as-pass)
   - `run_evaluator()` already printed the verdict, wrote the log file, and returned the correct exit code
   - The entire block from line 1734 to 1794 (find log file, re-parse verdict, report verdict) is redundant
   - Replace with: trust `run_evaluator()`'s exit code, print success message, return 0

2. **Simplify `cli.review()`** — already clean after ADV-0066 (lines 1861-1869)
   - `review()` already trusts `run_evaluator()` and doesn't duplicate verdict extraction
   - Verify no further action needed (it's the model for how `evaluate()` should look)

3. **Add empty `test_command` guard in `cli.validate()`** (line 1895-1897)
   - `shlex.split("")` returns `[]`, causing `subprocess.run([])` to raise `ValueError`
   - Add guard: `if not test_command or not test_command.strip():`
   - Print actionable error message and return 1

4. **Harden `output_suffix` fallback** (line 1738) — optional
   - Change `builtin_config.output_suffix or "EVALUATE"` to also catch empty string
   - `builtin_config.output_suffix.strip() if builtin_config.output_suffix else "EVALUATE"`
   - Or leave as-is (all current builtins have non-empty suffixes)

### Non-Functional Requirements
- [ ] No behavior change for happy paths — evaluate/review/validate produce same output
- [ ] Dead code removed, not just commented out
- [ ] Tests updated to reflect simplified evaluate() flow

## TDD Workflow (Mandatory)

### Test Requirements
- [ ] Test: `evaluate()` returns 0 when `run_evaluator()` returns 0 (no re-parsing)
- [ ] Test: `evaluate()` returns non-zero when `run_evaluator()` returns non-zero
- [ ] Test: `validate("")` returns 1 with actionable error (not ValueError)
- [ ] Test: `validate("  ")` returns 1 with actionable error (not ValueError)
- [ ] Test: `validate(None)` falls back to config default (existing behavior preserved)
- [ ] Existing evaluate/review/validate tests still pass
- [ ] Coverage: 80%+ for modified code

**Test files to modify**:
- `tests/test_cli_core.py` — Update evaluate() tests, add validate() edge case tests
- `tests/test_evaluate.py` — Update evaluate() tests that check verdict output

## Implementation Plan

### Step 1: Write Tests (Red)

Add tests for:
- `evaluate()` success path: mock `run_evaluator` returning 0, verify evaluate() returns 0 without calling `validate_evaluation_output`
- `evaluate()` failure path: mock `run_evaluator` returning 1, verify evaluate() returns 1
- `validate("")`: verify returns 1 with error message, no ValueError
- `validate("  ")`: same

### Step 2: Simplify `cli.evaluate()` (Green)

**Before** (lines 1727-1794 — 67 lines):
```python
eval_result = run_evaluator(builtin_config, task_file)
if eval_result != 0:
    print("📋 Evaluation complete (needs revision)")
    return eval_result

# Find the output log file by evaluator suffix  ← REDUNDANT
log_dir = config.get(...)                        ← REDUNDANT
suffix = builtin_config.output_suffix or ...     ← REDUNDANT
log_files = sorted(glob.glob(...))               ← REDUNDANT
...                                              ← REDUNDANT
is_valid, verdict, message = validate_evaluation_output(log_file)  ← REDUNDANT
... 40 lines of verdict handling ...             ← DEAD CODE
```

**After** (~10 lines):
```python
eval_result = run_evaluator(builtin_config, task_file)
if eval_result != 0:
    print()
    print("📋 Evaluation complete (needs revision)")
    print(f"   Details: {config.get('log_directory', '.adversarial/logs/')}")
    return eval_result

print()
print(f"{GREEN}✅ Evaluation approved!{RESET}")
return 0
```

This matches the pattern already used by `review()` (lines 1861-1869).

### Step 3: Add `validate()` Guard

**Before**:
```python
result = subprocess.run(
    shlex.split(test_command),
    timeout=600,
)
```

**After**:
```python
if not test_command or not test_command.strip():
    print(f"{RED}❌ ERROR: Test command is empty{RESET}")
    print("   Fix: Provide a test command or set test_command in .adversarial/config.yml")
    return 1

result = subprocess.run(
    shlex.split(test_command),
    timeout=600,
)
```

### Step 4: Clean Up

- Remove `import glob` that was only used for the deleted log-file search in `evaluate()`
- Remove `validate_evaluation_output` import if no longer used in cli.py (check other callers)
- Remove `verify_token_count` call if it was only used in the deleted block
- Run full test suite

## Acceptance Criteria

### Must Have
- [ ] `cli.evaluate()` no longer calls `validate_evaluation_output()` or `glob.glob()` for log file search
- [ ] `cli.evaluate()` trusts `run_evaluator()` exit code entirely
- [ ] NEEDS_REVISION and REJECTED dead code branches removed from `evaluate()`
- [ ] `validate("")` returns 1 with error message (no ValueError)
- [ ] All tests passing
- [ ] No regressions in existing evaluate/review/validate behavior

### Should Have
- [ ] `evaluate()` and `review()` follow the same pattern (consistency)
- [ ] `verify_token_count()` call removed if orphaned
- [ ] Unused imports cleaned up

## Success Metrics

### Quantitative
- Lines removed from `cli.evaluate()`: ~55 (67 → ~12)
- Test pass rate: 100%
- Dead code branches eliminated: 3 (NEEDS_REVISION, REJECTED, invalid-output in evaluate())

### Qualitative
- `evaluate()` and `review()` follow identical patterns
- Single responsibility: `run_evaluator()` owns verdict handling, CLI owns user-facing messages
- Defensive: `validate()` handles edge cases gracefully

## Time Estimate

| Phase | Time | Status |
|-------|------|--------|
| Write tests (evaluate simplification + validate guard) | 0.5 hours | [ ] |
| Simplify cli.evaluate() | 0.5 hours | [ ] |
| Add validate() guard | 0.25 hours | [ ] |
| Clean up imports + verify | 0.25 hours | [ ] |
| Full test suite | 0.5 hours | [ ] |
| **Total** | **2 hours** | [ ] |

## PR Plan

Single PR — ~70 lines changed, ~55 removed. Very small scope.

**Branch**: `feature/ADV-0067-fix-cli-preexisting-issues`

## References

- **Source**: `.agent-context/ADV-0066-preexisting-issues.md`
- **Current evaluate()**: `adversarial_workflow/cli.py:1697-1794`
- **Current review()**: `adversarial_workflow/cli.py:1797-1869` (model pattern)
- **Current validate()**: `adversarial_workflow/cli.py:1872-1914`
- **Runner contract**: `adversarial_workflow/evaluators/runner.py:32-44, 190-213`
- **Testing**: `pytest tests/ -v`
- **Coverage**: `pytest tests/ --cov=adversarial_workflow`

---

**Template Version**: 2.0.0
**Project**: adversarial-workflow
**Last Updated**: 2026-04-13
