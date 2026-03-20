# ADV-0057: Review Script Robustness - Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-03-19
**From**: Planner
**To**: feature-developer-v3
**Task**: delegation/tasks/2-todo/ADV-0057-review-script-robustness.md
**Status**: Ready for implementation
**Evaluation**: N/A (small hardening task, 4 specific fixes)

---

## Task Summary

Fix 4 robustness gaps in `review_implementation.sh` and its CLI wrapper, identified by the adversarial code-review evaluator during ADV-0054. All are pre-existing edge cases, not regressions.

## Current Situation

The review script (`review_implementation.sh`) and its template work fine in normal conditions but fail ungracefully when:
1. Config is missing `artifacts_directory` or `log_directory`
2. The repo uses `master` instead of `main` and `origin/HEAD` isn't set
3. `git diff base...HEAD` fails with invalid refs
4. Script is invoked directly with empty `TASK_FILE`

These were found by the Gemini Flash code-reviewer during ADV-0054 review.

## Your Mission

Apply 4 targeted fixes across 3 files. Each fix is small and independent.

### Fix 1: Default config variables (Medium risk)
**Files**: `.adversarial/scripts/review_implementation.sh` + template
**Change**: Add default values after config parsing:
```bash
ARTIFACTS_DIR=${ARTIFACTS_DIR:-.adversarial/artifacts/}
LOG_DIR=${LOG_DIR:-.adversarial/logs/}
```

### Fix 2: Validate default branch ref exists (Low risk)
**Files**: `.adversarial/scripts/review_implementation.sh` + template
**Change**: After determining `DEFAULT_BRANCH`, verify it exists:
```bash
if ! git rev-parse --verify "$DEFAULT_BRANCH" >/dev/null 2>&1; then
  echo "Error: Cannot find base branch '$DEFAULT_BRANCH'. Set origin/HEAD or pass branch explicitly."
  exit 1
fi
```

### Fix 3: CLI pre-check error handling (Low risk)
**Files**: `adversarial_workflow/cli.py` (the `review()` function, around line 2157)
**Change**: Check `branch_diff.returncode` for values > 1 (git error vs. changes detected) and report clearly before invoking the script.

### Fix 4: Empty task_file validation (Low risk)
**Files**: `.adversarial/scripts/review_implementation.sh` + template
**Change**: Add early validation:
```bash
if [ -z "$TASK_FILE" ] || [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found or not specified: $TASK_FILE"
  exit 1
fi
```

## Critical Details

### Template sync is mandatory
The script at `.adversarial/scripts/review_implementation.sh` and the template at `adversarial_workflow/templates/review_implementation.sh.template` **must stay in sync**. Apply identical changes to both files.

### Files to modify
1. `.adversarial/scripts/review_implementation.sh` — fixes 1, 2, 4
2. `adversarial_workflow/templates/review_implementation.sh.template` — same fixes 1, 2, 4
3. `adversarial_workflow/cli.py` — fix 3 (review function ~line 2157)

### Testing
- All 500 existing tests must pass
- Add tests for fix 3 (CLI error handling) if feasible
- Shell script fixes are harder to unit test — manual verification is acceptable

## Defensive Coding Rules

- Check `.agent-context/patterns.yml` before writing code
- Use `==` for identifier comparison (DK002)
- Run `python3 scripts/core/pattern_lint.py` on any modified `.py` files
- Run `.venv/bin/python -m pytest tests/ -q` to verify no regressions

## Success Criteria

- All 4 edge cases handled gracefully with clear error messages
- Template and committed script remain in sync
- All existing tests pass
- No unrelated changes

---

**Task File**: `delegation/tasks/2-todo/ADV-0057-review-script-robustness.md`
**Evaluator Review**: `.agent-context/reviews/ADV-0054-code-reviewer-fast.md`
**Handoff Date**: 2026-03-19
**Coordinator**: Planner
