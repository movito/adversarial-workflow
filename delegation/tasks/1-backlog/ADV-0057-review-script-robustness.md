# ADV-0057: Review Script Robustness Improvements

**Status**: Backlog
**Priority**: Medium
**Type**: Enhancement
**Estimated Effort**: 1-2 hours
**Created**: 2026-03-15
**Origin**: ADV-0054 code-reviewer-fast evaluator findings

## Summary

The adversarial code-review evaluator (Gemini Flash) identified 4 robustness
gaps in `review_implementation.sh` and its CLI wrapper during the ADV-0054
review. All are pre-existing edge cases (not regressions), but worth hardening.

## Issues to Address

### 1. Empty `ARTIFACTS_DIR` / `LOG_DIR` from config parsing

**Risk**: Medium
**Files**: `review_implementation.sh`, template

If `artifacts_directory` or `log_directory` is missing from `.adversarial/config.yml`,
the variables are empty strings. `mkdir -p ""` creates nothing useful, and subsequent
file writes go to unexpected paths.

**Fix**: Add validation after config parsing:
```bash
ARTIFACTS_DIR=${ARTIFACTS_DIR:-.adversarial/artifacts/}
LOG_DIR=${LOG_DIR:-.adversarial/logs/}
```

### 2. Non-existent default branch fallback

**Risk**: Low
**Files**: `review_implementation.sh`, template, `cli.py`

If `origin/HEAD` is not set AND the repo uses `master` (not `main`), the fallback
to `main` causes `git diff main...HEAD` to fail.

**Fix**: After setting `DEFAULT_BRANCH`, verify the ref exists:
```bash
if ! git rev-parse --verify "$DEFAULT_BRANCH" >/dev/null 2>&1; then
  echo "Error: Cannot find base branch '$DEFAULT_BRANCH'. Set origin/HEAD or pass branch explicitly."
  exit 1
fi
```

### 3. CLI pre-check error handling

**Risk**: Low
**Files**: `adversarial_workflow/cli.py` (`review()`)

When `git diff base...HEAD` fails due to invalid refs, the non-zero exit code
correctly prevents the "no changes" abort, but the script then crashes with an
unhelpful git error. The CLI could catch this and provide a better message.

**Fix**: Check `branch_diff.returncode` for values > 1 (git error vs changes detected)
and report the issue before invoking the script.

### 4. Invalid `task_file` edge cases in bash script

**Risk**: Low
**Files**: `review_implementation.sh`, template

The script validates file existence but doesn't handle empty strings well
(`basename "" .md` produces `.`). The CLI now requires `task_file`, so this
is only reachable if the script is invoked directly.

**Fix**: Add early validation:
```bash
if [ -z "$TASK_FILE" ] || [ ! -f "$TASK_FILE" ]; then
  echo "Error: Task file not found or not specified: $TASK_FILE"
  exit 1
fi
```

## Acceptance Criteria

- [ ] Config variables have sensible defaults when missing from config.yml
- [ ] Default branch fallback validates the ref exists before using it
- [ ] CLI provides clear error when git state is invalid for review
- [ ] Script handles empty/invalid task_file gracefully
- [ ] Template and committed script remain in sync
- [ ] All existing tests pass

## Notes

- These are all pre-existing issues, not regressions from ADV-0054
- Evaluator review: `.agent-context/reviews/ADV-0054-code-reviewer-fast.md`
- Consider adding integration tests for the review script if feasible
